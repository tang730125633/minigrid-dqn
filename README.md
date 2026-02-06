# MiniGrid DQN: Reinforcement Learning with Reward Shaping

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Deep Q-Network (DQN) agent for the MiniGrid-Empty-8x8-v0 environment, with Potential-Based Reward Shaping (PBRS) improvement and ablation studies.

## 🚀 快速开始（推荐）

### Windows 用户
👉 查看 [**Windows 快速开始指南**](README_WINDOWS.md)

1. 下载项目并解压到桌面
2. **双击 `安装并启动.bat`**
3. 浏览器自动打开可视化界面

### macOS / Linux 用户
```bash
git clone <repository-url>
cd minigrid-dqn
bash 安装并启动.sh
```

## 🌐 Web 可视化界面

本项目包含一个 **Streamlit Web 界面**，无需编程即可：
- 📊 查看训练曲线和成功率对比
- 🎬 观看智能体学习过程的动画
- ⚙️ 一键运行新实验
- 📈 对比不同算法的性能

启动后访问 http://localhost:8501

## Project Structure

```
minigrid-dqn/
├── configs/                 # Experiment configurations (YAML)
│   ├── default.yaml         # Baseline DQN
│   ├── reward_shaping.yaml  # DQN + PBRS
│   ├── ablation_gamma.yaml  # Ablation: gamma values
│   └── ablation_no_target.yaml  # Ablation: no target network
├── src/                     # Source code
│   ├── config.py            # Configuration loading
│   ├── env_utils.py         # Environment wrappers (RewardShaping, ObsPreprocess)
│   ├── network.py           # CNN Q-Network
│   ├── replay_buffer.py     # Experience replay buffer
│   ├── dqn_agent.py         # DQN agent
│   ├── train.py             # Training loop
│   ├── evaluate.py          # Evaluation script
│   └── visualize.py         # Chart and GIF generation
├── scripts/                 # Automation scripts (.sh + .bat)
├── results/                 # Training results (auto-generated)
├── logs/                    # TensorBoard logs (auto-generated)
├── figures/                 # Comparison charts (auto-generated)
└── gifs/                    # Demo GIFs (auto-generated)
```

## Requirements

- Python 3.8+
- PyTorch >= 2.0
- CPU only (no GPU required)

## Setup

### Windows

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

### macOS / Linux

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Run all experiments (recommended)

**Windows:**
```bash
scripts\train_all.bat
scripts\evaluate_all.bat
scripts\generate_report.bat
```

**macOS / Linux:**
```bash
bash scripts/train_all.sh
bash scripts/evaluate_all.sh
bash scripts/generate_report.sh
```

### Run a single experiment

```bash
# Baseline DQN
python -m src.train --config configs/default.yaml --seed 0

# DQN + Reward Shaping
python -m src.train --config configs/reward_shaping.yaml --seed 0

# Ablation: different gamma
python -m src.train --config configs/ablation_gamma.yaml --seed 0 --gamma 0.9

# Ablation: no target network
python -m src.train --config configs/ablation_no_target.yaml --seed 0
```

### Evaluate trained models

```bash
python -m src.evaluate --results_dir results --num_episodes 100
```

### Generate charts and GIFs

```bash
python -m src.visualize
```

### Monitor training with TensorBoard

```bash
tensorboard --logdir logs
```

## Method

### Baseline: DQN

Standard Deep Q-Network with:
- CNN architecture for 7x7x3 MiniGrid observations
- Experience replay (buffer size: 100k)
- Target network (updated every 1000 steps)
- Linear epsilon decay (1.0 → 0.01 over 20k steps)

### Improvement: Potential-Based Reward Shaping (PBRS)

Adds a shaping reward based on Manhattan distance to goal:

```
r_shaped = r_original + gamma * Phi(s') - Phi(s)
Phi(s) = 1 - (manhattan_distance_to_goal / max_distance)
```

This guides exploration toward the goal while preserving optimal policy (Ng et al., 1999).

### Ablation Studies

1. **Gamma sensitivity**: gamma ∈ {0.9, 0.99, 0.999} — tests how discount factor affects PBRS
2. **Target network**: with vs without — demonstrates DQN stabilization

Main comparison: 3 seeds (0, 1, 2), reporting mean ± std. Ablation studies: 1 seed.

## Results

### Main Comparison (3 seeds)

| Method | Seed 0 | Seed 1 | Seed 2 | Mean ± Std |
|--------|--------|--------|--------|------------|
| Baseline DQN | 0% | 100% | 100% | 66.7% ± 47.1% |
| **DQN + PBRS** | **100%** | **100%** | **100%** | **100% ± 0%** |

### Ablation: Gamma

| Gamma | Success Rate |
|-------|-------------|
| 0.9 | 100% |
| 0.99 | 100% |
| 0.999 | 100% |

### Ablation: Target Network

| Configuration | Success Rate |
|---------------|-------------|
| With target network | 100% |
| Without target network | 0% |

## Key Hyperparameters

| Parameter | Value |
|-----------|-------|
| Learning rate | 1e-4 |
| Gamma | 0.99 |
| Batch size | 64 |
| Buffer size | 100,000 |
| Epsilon decay | 20,000 steps |
| Target update | Every 1,000 steps |
| Training episodes | 3,000 |
| Evaluation episodes | 100 |

## References

- Mnih et al., 2015. "Human-level control through deep reinforcement learning." Nature.
- Ng et al., 1999. "Policy invariance under reward transformations." ICML.
- Chevalier-Boisvert et al., 2023. "Minigrid & Miniworld: Modular & Customizable RL Environments." NeurIPS.
