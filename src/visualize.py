"""Visualization: training curves, comparison charts, and GIF generation."""
import sys
import argparse
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def load_training_log(csv_path):
    """Load training log CSV."""
    episodes, rewards, eval_srs, eval_rewards, losses = [], [], [], [], []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            episodes.append(int(row["episode"]))
            rewards.append(float(row["episode_reward"]))
            losses.append(float(row["loss"]) if row["loss"] else 0)
            if row["eval_success_rate"]:
                eval_srs.append((int(row["episode"]), float(row["eval_success_rate"])))
            if row["eval_avg_reward"]:
                eval_rewards.append((int(row["episode"]), float(row["eval_avg_reward"])))
    return {
        "episodes": np.array(episodes),
        "rewards": np.array(rewards),
        "losses": np.array(losses),
        "eval_srs": eval_srs,
        "eval_rewards": eval_rewards,
    }


def smooth(data, window=100):
    """Moving average smoothing."""
    if len(data) < window:
        return data
    kernel = np.ones(window) / window
    return np.convolve(data, kernel, mode="valid")


def plot_training_curves(results_dir, figures_dir, experiments):
    """Plot training reward curves for multiple experiments."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for exp_name, label, color in experiments:
        logs = []
        for d in sorted(results_dir.iterdir()):
            if d.is_dir() and exp_name in d.name:
                csv_path = d / "training_log.csv"
                if csv_path.exists():
                    logs.append(load_training_log(csv_path))

        if not logs:
            continue

        # Reward curves
        min_len = min(len(log["rewards"]) for log in logs)
        all_rewards = np.array([smooth(log["rewards"][:min_len]) for log in logs])
        mean_r = np.mean(all_rewards, axis=0)
        std_r = np.std(all_rewards, axis=0)
        x = np.arange(len(mean_r))

        axes[0].plot(x, mean_r, label=label, color=color)
        axes[0].fill_between(x, mean_r - std_r, mean_r + std_r, alpha=0.2, color=color)

        # Eval success rate
        for log in logs:
            if log["eval_srs"]:
                eps, srs = zip(*log["eval_srs"])
                axes[1].plot(eps, srs, alpha=0.3, color=color)
        # Mean eval SR
        if logs[0]["eval_srs"]:
            all_srs = {}
            for log in logs:
                for ep, sr in log["eval_srs"]:
                    all_srs.setdefault(ep, []).append(sr)
            eps_sorted = sorted(all_srs.keys())
            mean_srs = [np.mean(all_srs[ep]) for ep in eps_sorted]
            axes[1].plot(eps_sorted, mean_srs, label=label, color=color, linewidth=2)

    axes[0].set_xlabel("Episode (smoothed)")
    axes[0].set_ylabel("Episode Reward")
    axes[0].set_title("Training Reward Curves")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel("Episode")
    axes[1].set_ylabel("Success Rate")
    axes[1].set_title("Evaluation Success Rate")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim(-0.05, 1.05)

    plt.tight_layout()
    fig.savefig(figures_dir / "training_curves.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {figures_dir / 'training_curves.png'}")


def plot_comparison_bar(results_dir, figures_dir):
    """Plot bar chart comparing final success rates."""
    summary_path = results_dir / "evaluation_summary.csv"
    if not summary_path.exists():
        print("No evaluation_summary.csv found. Run evaluate.py first.")
        return

    # Group by experiment type
    groups = {}
    with open(summary_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["experiment"]
            # Extract base name (remove seed suffix)
            base = name.rsplit("_seed", 1)[0]
            groups.setdefault(base, []).append(float(row["success_rate"]))

    labels = []
    means = []
    stds = []
    for base, rates in sorted(groups.items()):
        labels.append(base.replace("_", "\n"))
        means.append(np.mean(rates))
        stds.append(np.std(rates))

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 2), 6))
    x = np.arange(len(labels))
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=plt.cm.Set2(np.linspace(0, 1, len(labels))))

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Success Rate")
    ax.set_title("Final Evaluation: Success Rate Comparison (3 seeds)")
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3, axis="y")

    # Value labels
    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.02,
                f"{mean:.1%}", ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    fig.savefig(figures_dir / "comparison_bar.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {figures_dir / 'comparison_bar.png'}")


def plot_ablation_gamma(results_dir, figures_dir):
    """Plot ablation study for gamma values."""
    summary_path = results_dir / "evaluation_summary.csv"
    if not summary_path.exists():
        return

    gamma_results = {}
    with open(summary_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["experiment"]
            if "ablation_gamma" in name:
                # Extract gamma value
                parts = name.split("gamma")
                if len(parts) > 1:
                    gamma_str = parts[-1].split("_seed")[0]
                    try:
                        gamma = float(gamma_str)
                        gamma_results.setdefault(gamma, []).append(float(row["success_rate"]))
                    except ValueError:
                        pass

    if not gamma_results:
        print("No ablation_gamma results found")
        return

    gammas = sorted(gamma_results.keys())
    means = [np.mean(gamma_results[g]) for g in gammas]
    stds = [np.std(gamma_results[g]) for g in gammas]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(range(len(gammas)), means, yerr=stds, fmt="o-", capsize=5, markersize=8, linewidth=2)
    ax.set_xticks(range(len(gammas)))
    ax.set_xticklabels([str(g) for g in gammas])
    ax.set_xlabel("Gamma")
    ax.set_ylabel("Success Rate")
    ax.set_title("Ablation Study: Effect of Gamma on Success Rate")
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3)

    for i, (m, s) in enumerate(zip(means, stds)):
        ax.annotate(f"{m:.1%}", (i, m + s + 0.03), ha="center", fontweight="bold")

    plt.tight_layout()
    fig.savefig(figures_dir / "ablation_gamma.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {figures_dir / 'ablation_gamma.png'}")


def plot_ablation_target(results_dir, figures_dir):
    """Plot ablation study for target network."""
    summary_path = results_dir / "evaluation_summary.csv"
    if not summary_path.exists():
        return

    groups = {"With Target Net": [], "Without Target Net": []}
    with open(summary_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["experiment"]
            if "ablation_no_target" in name:
                groups["Without Target Net"].append(float(row["success_rate"]))
            elif "reward_shaping" in name and "ablation" not in name:
                groups["With Target Net"].append(float(row["success_rate"]))

    labels = list(groups.keys())
    means = [np.mean(v) if v else 0 for v in groups.values()]
    stds = [np.std(v) if v else 0 for v in groups.values()]

    if all(m == 0 for m in means):
        print("No target network ablation results found")
        return

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(labels, means, yerr=stds, capsize=5, color=["#2196F3", "#FF5722"], width=0.5)
    ax.set_ylabel("Success Rate")
    ax.set_title("Ablation Study: Target Network Effect")
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3, axis="y")

    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 0.02,
                f"{mean:.1%}", ha="center", va="bottom", fontweight="bold")

    plt.tight_layout()
    fig.savefig(figures_dir / "ablation_target_network.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {figures_dir / 'ablation_target_network.png'}")


def generate_gif(results_dir, gifs_dir):
    """Generate demo GIFs from recorded frames."""
    try:
        import imageio
    except ImportError:
        print("imageio not installed, skipping GIF generation")
        return

    for exp_dir in sorted(results_dir.iterdir()):
        if not exp_dir.is_dir():
            continue
        frames_dir = exp_dir / "frames"
        if not frames_dir.exists():
            continue

        for npy_file in sorted(frames_dir.glob("*.npy")):
            frames = np.load(npy_file)
            gif_name = f"{exp_dir.name}_{npy_file.stem}.gif"
            gif_path = gifs_dir / gif_name
            imageio.mimsave(str(gif_path), frames, fps=5, loop=0)
            print(f"Saved GIF: {gif_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate visualizations")
    parser.add_argument("--results_dir", type=str, default=None, help="Results directory")
    parser.add_argument("--figures_dir", type=str, default=None, help="Output figures directory")
    parser.add_argument("--gifs_dir", type=str, default=None, help="Output GIFs directory")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    results_dir = Path(args.results_dir) if args.results_dir else project_root / "results"
    figures_dir = Path(args.figures_dir) if args.figures_dir else project_root / "figures"
    gifs_dir = Path(args.gifs_dir) if args.gifs_dir else project_root / "gifs"

    figures_dir.mkdir(parents=True, exist_ok=True)
    gifs_dir.mkdir(parents=True, exist_ok=True)

    print("Generating visualizations...")
    print(f"Results: {results_dir}")
    print(f"Figures: {figures_dir}")
    print()

    # Main comparison
    plot_training_curves(results_dir, figures_dir, [
        ("baseline", "Baseline DQN", "#2196F3"),
        ("reward_shaping", "DQN + Reward Shaping", "#4CAF50"),
    ])

    plot_comparison_bar(results_dir, figures_dir)

    # Ablation studies
    plot_ablation_gamma(results_dir, figures_dir)
    plot_ablation_target(results_dir, figures_dir)

    # GIFs
    generate_gif(results_dir, gifs_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
