"""Training loop with logging."""
import sys
import os
import time
import csv
import random
import numpy as np
import torch
from pathlib import Path
from torch.utils.tensorboard import SummaryWriter

# Force unbuffered output for real-time progress
os.environ["PYTHONUNBUFFERED"] = "1"

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import parse_args
from src.env_utils import make_env
from src.dqn_agent import DQNAgent


def set_seed(seed):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def evaluate(agent, config, num_episodes=20):
    """Evaluate agent without exploration."""
    env = make_env(config, reward_shaping=False)  # Always evaluate without shaping
    successes = 0
    total_rewards = []

    for _ in range(num_episodes):
        obs, _ = env.reset()
        episode_reward = 0
        done = False

        while not done:
            action = agent.select_action(obs, evaluate=True)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            done = terminated or truncated

        total_rewards.append(episode_reward)
        if terminated and episode_reward > 0:
            successes += 1

    env.close()
    return successes / num_episodes, np.mean(total_rewards)


def train(config):
    """Main training loop."""
    seed = config["seed"]
    set_seed(seed)

    # Setup directories
    project_root = Path(__file__).resolve().parent.parent
    exp_name = f"{config['experiment_name']}_seed{seed}"
    output_dir = Path(config.get("output_dir", project_root / "results")) / exp_name
    log_dir = project_root / "logs" / exp_name
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create environment
    use_shaping = config["reward_shaping"]["enabled"]
    env = make_env(config, reward_shaping=use_shaping)

    # Create agent
    obs_shape = env.observation_space.shape
    n_actions = env.action_space.n
    agent = DQNAgent(obs_shape, n_actions, config)

    # Logging
    writer = SummaryWriter(str(log_dir))
    csv_path = output_dir / "training_log.csv"
    with open(csv_path, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([
            "episode", "steps", "epsilon", "episode_reward",
            "episode_length", "loss", "eval_success_rate", "eval_avg_reward",
        ])

    print(f"Training: {exp_name}", flush=True)
    print(f"  Environment: {config['env']['name']}", flush=True)
    print(f"  Reward Shaping: {use_shaping}", flush=True)
    print(f"  Target Network: {config['agent']['use_target_network']}", flush=True)
    print(f"  Gamma: {config['agent']['gamma']}", flush=True)
    print(f"  Seed: {seed}")
    print(f"  Output: {output_dir}")
    print()

    start_time = time.time()
    total_steps = 0
    recent_rewards = []
    recent_losses = []

    num_episodes = config["training"]["num_episodes"]
    eval_freq = config["training"]["eval_freq"]
    log_freq = config["training"]["log_freq"]
    save_freq = config["training"]["save_freq"]

    for episode in range(1, num_episodes + 1):
        obs, _ = env.reset()
        episode_reward = 0
        episode_original_reward = 0
        episode_length = 0
        episode_loss = 0
        loss_count = 0
        done = False

        while not done:
            action = agent.select_action(obs)
            next_obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            # Track original reward for logging
            original_reward = info.get("original_reward", reward)
            episode_original_reward += original_reward

            agent.store_transition(obs, action, reward, next_obs, float(done))
            # Update every 4 steps to speed up training
            loss = agent.update() if total_steps % 4 == 0 else None

            if loss is not None:
                episode_loss += loss
                loss_count += 1

            obs = next_obs
            episode_reward += reward
            episode_length += 1
            total_steps += 1

        avg_loss = episode_loss / max(loss_count, 1)
        recent_rewards.append(episode_original_reward)
        recent_losses.append(avg_loss)

        # TensorBoard logging
        writer.add_scalar("train/episode_reward", episode_original_reward, episode)
        writer.add_scalar("train/episode_length", episode_length, episode)
        writer.add_scalar("train/epsilon", agent.epsilon, episode)
        writer.add_scalar("train/loss", avg_loss, episode)
        if use_shaping:
            writer.add_scalar("train/shaped_reward", episode_reward, episode)

        # Console + CSV logging
        eval_sr, eval_ar = None, None
        if episode % eval_freq == 0:
            eval_sr, eval_ar = evaluate(agent, config, config["training"]["eval_episodes"])
            writer.add_scalar("eval/success_rate", eval_sr, episode)
            writer.add_scalar("eval/avg_reward", eval_ar, episode)

        if episode % log_freq == 0:
            avg_recent = np.mean(recent_rewards[-log_freq:])
            elapsed = time.time() - start_time
            eps_per_sec = episode / elapsed

            status = (
                f"Ep {episode:>6d}/{num_episodes} | "
                f"Steps {total_steps:>8d} | "
                f"Eps {agent.epsilon:.3f} | "
                f"Avg R(100) {avg_recent:.3f} | "
                f"Loss {np.mean(recent_losses[-log_freq:]):.4f}"
            )
            if eval_sr is not None:
                status += f" | Eval SR {eval_sr:.2%} | Eval R {eval_ar:.3f}"
            status += f" | {eps_per_sec:.0f} ep/s"
            print(status, flush=True)

        # CSV logging
        with open(csv_path, "a", newline="") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([
                episode, total_steps, f"{agent.epsilon:.4f}",
                f"{episode_original_reward:.4f}", episode_length,
                f"{avg_loss:.6f}",
                f"{eval_sr:.4f}" if eval_sr is not None else "",
                f"{eval_ar:.4f}" if eval_ar is not None else "",
            ])

        # Save checkpoint
        if episode % save_freq == 0:
            agent.save(output_dir / f"checkpoint_ep{episode}.pt")

    # Final save
    agent.save(output_dir / "final_model.pt")
    writer.close()
    env.close()

    # Final evaluation
    print("\n--- Final Evaluation ---")
    final_sr, final_ar = evaluate(agent, config, num_episodes=100)
    print(f"Success Rate: {final_sr:.2%}")
    print(f"Avg Reward:   {final_ar:.4f}")

    # Save final results
    results_path = output_dir / "final_results.txt"
    with open(results_path, "w") as f:
        f.write(f"experiment: {exp_name}\n")
        f.write(f"success_rate: {final_sr:.4f}\n")
        f.write(f"avg_reward: {final_ar:.4f}\n")
        f.write(f"total_episodes: {num_episodes}\n")
        f.write(f"total_steps: {total_steps}\n")
        f.write(f"training_time: {time.time() - start_time:.1f}s\n")

    print(f"\nResults saved to {output_dir}")
    return final_sr, final_ar


if __name__ == "__main__":
    config = parse_args()
    train(config)
