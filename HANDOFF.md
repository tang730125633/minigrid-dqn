# 交接文档 — MiniGrid DQN 强化学习项目

## 项目背景

这是一个**大学作业项目**，需要在 1-2 周内完成一个强化学习游戏智能体。客户要求：
1. 包含 **baseline 对比实验**和**消融实验**
2. 项目打包为 **zip** 发给客户，客户在 **Windows** 电脑上解压后能直接运行
3. 代码跨平台兼容（已提供 `.bat` + `.sh` 脚本）

## 当前状态：✅ 全部完成，可以交付

### 已完成的部分

| 项目 | 状态 | 说明 |
|------|------|------|
| 项目结构 | ✅ 完成 | 见下方目录树 |
| 4 个配置文件 (YAML) | ✅ 完成 | `configs/` 目录 |
| 8 个源代码文件 | ✅ 完成 | `src/` 目录 |
| 6 个脚本 (.sh + .bat) | ✅ 完成 | `scripts/` 目录 |
| README.md | ✅ 完成 | 英文使用说明 |
| requirements.txt | ✅ 完成 | 所有依赖 |
| **全量训练** | ✅ 完成 | 10 个实验全部跑完 |
| **评估** | ✅ 完成 | 100 episodes 评估 |
| **图表** | ✅ 完成 | 4 张对比图 |
| **GIF** | ✅ 完成 | 50 个演示 GIF |

### 可能需要调整的部分

| 优先级 | 任务 | 说明 |
|--------|------|------|
| **P1** | 更新 README 中的结果表格 | 用实际数据替换预期数据 |
| **P2** | 打包 zip 交付 | 排除 venv/, __pycache__/, logs/, HANDOFF.md |
| **P3** | 根据客户反馈调整 | 可能需要增加/减少实验 |

## 实际实验结果

### 主要对比实验 (Baseline vs Reward Shaping, 3 seeds)

| 方法 | Seed 0 | Seed 1 | Seed 2 | Mean ± Std |
|------|--------|--------|--------|------------|
| **Baseline DQN** | 0% | 100% | 100% | **66.7% ± 47.1%** |
| **DQN + Reward Shaping** | 100% | 100% | 100% | **100% ± 0%** |

**关键发现**:
- Reward Shaping 在 ~1000 episode 就达到 100% 成功率，非常稳定
- Baseline 高度不稳定：1/3 seed 完全不收敛，另外 2 个在训练后期才勉强收敛
- 训练曲线图清楚展示了这种差异

### 消融实验 A — Gamma 值

| Gamma | Success Rate | 备注 |
|-------|-------------|------|
| 0.9 | 100% | PBRS 对低 gamma 也有效 |
| 0.99 | 100% | 默认值，表现最佳 |
| 0.999 | 100% | 高 gamma 同样有效 |

**结论**: 在 MiniGrid-Empty-8x8 这个简单环境中，gamma 值对 PBRS 效果影响不大。三个值都能达到 100%。

### 消融实验 B — Target Network

| 配置 | Success Rate | Loss 稳定性 |
|------|-------------|------------|
| **有 Target Network** | 100% | 稳定，loss ~0.003 |
| **无 Target Network** | 0% | 极不稳定，loss 飙到 8.14 |

**结论**: Target Network 对训练稳定性至关重要。没有它，即使有 Reward Shaping 也无法学习。

### 生成的图表

1. `figures/training_curves.png` — 训练奖励曲线 + 评估成功率对比
2. `figures/comparison_bar.png` — 所有实验最终成功率柱状图
3. `figures/ablation_gamma.png` — Gamma 消融实验图
4. `figures/ablation_target_network.png` — Target Network 消融实验图
5. `gifs/` — 50 个演示 GIF（每个实验 5 个 episode 的可视化）

## 项目结构

```
minigrid-dqn/
├── README.md                    # 英文使用说明（给客户看）
├── HANDOFF.md                   # 本交接文档（不给客户）
├── requirements.txt             # Python 依赖
├── configs/
│   ├── default.yaml             # Baseline DQN 超参
│   ├── reward_shaping.yaml      # DQN + Reward Shaping 超参
│   ├── ablation_gamma.yaml      # 消融实验: gamma 值
│   └── ablation_no_target.yaml  # 消融实验: 无 target network
├── src/
│   ├── __init__.py
│   ├── config.py                # 配置加载 + CLI 参数解析
│   ├── env_utils.py             # 环境封装 (RewardShapingWrapper + ObsPreprocessWrapper)
│   ├── network.py               # CNN Q-Network (~142k 参数)
│   ├── replay_buffer.py         # 经验回放缓冲区
│   ├── dqn_agent.py             # DQN 智能体核心 (epsilon-greedy, target network)
│   ├── train.py                 # 训练循环 (CSV + TensorBoard 日志)
│   ├── evaluate.py              # 评估脚本 (加载模型, 跑100局, 输出成功率)
│   └── visualize.py             # 可视化 (训练曲线, 对比柱状图, 消融图, GIF)
├── scripts/
│   ├── train_all.sh / .bat      # 一键训练所有实验
│   ├── evaluate_all.sh / .bat   # 一键评估
│   └── generate_report.sh / .bat # 一键生成图表
├── results/                     # ✅ 已有完整训练结果
│   ├── baseline_seed{0,1,2}/
│   ├── reward_shaping_seed{0,1,2}/
│   ├── ablation_gamma{0.9,0.99,0.999}_seed0/
│   ├── ablation_no_target_seed0/
│   └── evaluation_summary.csv
├── figures/                     # ✅ 已有 4 张图表
├── gifs/                        # ✅ 已有 50 个 GIF
├── logs/                        # TensorBoard 日志
└── venv/                        # Python 虚拟环境（不打包）
```

## 技术方案详解

### 环境: MiniGrid-Empty-8x8-v0
- 8x8 的空房间，智能体需要找到目标位置
- 观测: 7x7x3 的图像（部分可观测的 agent-centric 视角）
- 动作: 7 个离散动作（左转、右转、前进等）
- 奖励: 到达目标才有正奖励（稀疏奖励问题）

### 算法: DQN (Deep Q-Network)
- CNN 提取观测特征 → Q 值预测
- 经验回放 (Experience Replay) 打破样本相关性
- Target Network 稳定训练
- Epsilon-greedy 探索策略

### 改进: PBRS (Potential-Based Reward Shaping)
核心公式: `r_shaped = r_original + gamma * Phi(s') - Phi(s)`
- Phi(s) = 1 - (曼哈顿距离到目标 / 最大距离)
- 引导智能体往目标方向走，加速学习
- 理论保证不会改变最优策略 (Ng et al., 1999)
- 实现为 Gymnasium Wrapper，与算法完全解耦

### 关键超参数 (最终使用的值)

| 参数 | 值 |
|------|-----|
| Learning rate | 1e-4 |
| Gamma | 0.99 |
| Batch size | 64 |
| Buffer size | 100,000 |
| Epsilon decay | 20,000 steps |
| Target update | Every 1,000 steps |
| Training episodes | 3,000 |
| Update frequency | Every 4 steps |
| Evaluation episodes | 100 (final) |

## 如何复现

### 如果需要从头跑实验
```bash
# 1. 创建环境 (Python 3.10-3.13，不要用 3.14)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. 训练全部
bash scripts/train_all.sh  # Windows: scripts\train_all.bat

# 3. 评估
bash scripts/evaluate_all.sh

# 4. 生成图表
bash scripts/generate_report.sh
```

### 如果只需要重新生成图表
```bash
source venv/bin/activate
python -m src.visualize
```

## 打包交付

```bash
cd /Users/tang
zip -r minigrid-dqn.zip minigrid-dqn/ \
  -x "minigrid-dqn/venv/*" \
  -x "minigrid-dqn/src/__pycache__/*" \
  -x "minigrid-dqn/__pycache__/*" \
  -x "minigrid-dqn/logs/*" \
  -x "minigrid-dqn/HANDOFF.md" \
  -x "minigrid-dqn/.DS_Store"
```

## 重要注意事项

1. **Python 版本**: 3.10-3.13（3.14 与 pygame 不兼容）
2. **评估用 original_reward**: evaluate.py 已自动处理
3. **路径用 pathlib**: Windows 兼容
4. **Buffer 大小**: 从 50k 增加到 100k 防止了 catastrophic forgetting
5. **Update frequency**: 每 4 步更新一次梯度，显著提升训练速度
