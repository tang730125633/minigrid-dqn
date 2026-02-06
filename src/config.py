"""Configuration loading and management."""
import yaml
import argparse
from pathlib import Path


def load_config(config_path):
    """Load YAML config file and return as dict."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="MiniGrid DQN Training")
    parser.add_argument("--config", type=str, required=True, help="Path to config YAML")
    parser.add_argument("--seed", type=int, default=None, help="Override random seed")
    parser.add_argument("--gamma", type=float, default=None, help="Override gamma")
    parser.add_argument("--experiment_name", type=str, default=None, help="Override experiment name")
    parser.add_argument("--output_dir", type=str, default=None, help="Override output directory")
    args = parser.parse_args()

    config = load_config(args.config)

    # Apply CLI overrides
    if args.seed is not None:
        config["seed"] = args.seed
    if args.gamma is not None:
        config["agent"]["gamma"] = args.gamma
    if args.experiment_name is not None:
        config["experiment_name"] = args.experiment_name
    if args.output_dir is not None:
        config["output_dir"] = args.output_dir

    return config
