"""Evaluation script: load trained models and evaluate."""
import sys
import argparse
import csv
import random
import numpy as np
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import load_config
from src.env_utils import make_env
from src.dqn_agent import DQNAgent


def evaluate_model(model_path, config, num_episodes=100, record_episodes=False):
    """Evaluate a trained model."""
    env = make_env(config, reward_shaping=False)
    obs_shape = env.observation_space.shape
    n_actions = env.action_space.n

    agent = DQNAgent(obs_shape, n_actions, config)
    agent.load(model_path)

    results = []
    for ep in range(num_episodes):
        obs, _ = env.reset()
        episode_reward = 0
        episode_length = 0
        done = False
        frames = []

        while not done:
            if record_episodes and ep < 5:
                frames.append(env.unwrapped.get_frame())
            action = agent.select_action(obs, evaluate=True)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1
            done = terminated or truncated

        success = terminated and episode_reward > 0
        results.append({
            "episode": ep,
            "reward": episode_reward,
            "length": episode_length,
            "success": success,
            "frames": frames if record_episodes and ep < 5 else None,
        })

    env.close()
    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate trained DQN models")
    parser.add_argument("--results_dir", type=str, required=True, help="Path to results directory")
    parser.add_argument("--num_episodes", type=int, default=100, help="Number of eval episodes")
    parser.add_argument("--record", action="store_true", help="Record frames for GIF")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    project_root = Path(__file__).resolve().parent.parent

    # Find all experiment directories
    if not results_dir.exists():
        print(f"Results directory not found: {results_dir}")
        return

    experiments = sorted([d for d in results_dir.iterdir() if d.is_dir()])
    if not experiments:
        print("No experiment directories found")
        return

    print(f"Found {len(experiments)} experiments")
    print("=" * 70)

    summary = []
    for exp_dir in experiments:
        model_path = exp_dir / "final_model.pt"
        if not model_path.exists():
            print(f"  Skipping {exp_dir.name} (no final_model.pt)")
            continue

        # Determine config based on experiment name
        exp_name = exp_dir.name
        if "ablation_no_target" in exp_name:
            config_name = "ablation_no_target.yaml"
        elif "ablation_gamma" in exp_name:
            config_name = "ablation_gamma.yaml"
        elif "reward_shaping" in exp_name:
            config_name = "reward_shaping.yaml"
        else:
            config_name = "default.yaml"

        config_path = project_root / "configs" / config_name
        config = load_config(config_path)

        # Extract seed and gamma from directory name
        if "seed" in exp_name:
            seed_str = exp_name.split("seed")[-1].split("_")[0]
            try:
                config["seed"] = int(seed_str)
            except ValueError:
                pass

        if "gamma" in exp_name:
            parts = exp_name.split("gamma")
            if len(parts) > 1:
                gamma_str = parts[-1].split("_seed")[0]
                try:
                    config["agent"]["gamma"] = float(gamma_str)
                except ValueError:
                    pass

        random.seed(42)
        np.random.seed(42)
        torch.manual_seed(42)

        print(f"\nEvaluating: {exp_name}")
        results = evaluate_model(model_path, config, args.num_episodes, args.record)

        success_rate = np.mean([r["success"] for r in results])
        avg_reward = np.mean([r["reward"] for r in results])
        avg_length = np.mean([r["length"] for r in results])
        std_reward = np.std([r["reward"] for r in results])

        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Avg Reward:   {avg_reward:.4f} +/- {std_reward:.4f}")
        print(f"  Avg Length:   {avg_length:.1f}")

        summary.append({
            "experiment": exp_name,
            "success_rate": success_rate,
            "avg_reward": avg_reward,
            "std_reward": std_reward,
            "avg_length": avg_length,
        })

        # Save per-experiment results
        eval_csv = exp_dir / "eval_results.csv"
        with open(eval_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["episode", "reward", "length", "success"])
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "episode": r["episode"],
                    "reward": r["reward"],
                    "length": r["length"],
                    "success": r["success"],
                })

        # Save frames for GIF generation
        if args.record:
            frames_dir = exp_dir / "frames"
            frames_dir.mkdir(exist_ok=True)
            for r in results:
                if r["frames"]:
                    np.save(frames_dir / f"ep{r['episode']}_frames.npy", np.array(r["frames"]))

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Experiment':<40} {'Success%':>10} {'Avg R':>10} {'Std R':>10}")
    print("-" * 70)
    for s in summary:
        print(f"{s['experiment']:<40} {s['success_rate']:>9.1%} {s['avg_reward']:>10.4f} {s['std_reward']:>10.4f}")

    # Save summary CSV
    summary_path = results_dir / "evaluation_summary.csv"
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["experiment", "success_rate", "avg_reward", "std_reward", "avg_length"])
        writer.writeheader()
        writer.writerows(summary)
    print(f"\nSummary saved to {summary_path}")


if __name__ == "__main__":
    main()
