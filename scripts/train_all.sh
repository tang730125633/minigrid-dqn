#!/bin/bash
# Train all experiments: baseline, reward shaping, and ablation studies
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  MiniGrid DQN - Train All Experiments"
echo "=========================================="
echo "Project root: $PROJECT_ROOT"
echo ""

# 1. Baseline DQN (3 seeds)
echo ">>> [1/6] Baseline DQN (3 seeds)"
for SEED in 0 1 2; do
    echo "  Seed $SEED..."
    python -u -m src.train --config configs/default.yaml --seed $SEED \
        --experiment_name "baseline"
done

# 2. DQN + Reward Shaping (3 seeds)
echo ">>> [2/6] DQN + Reward Shaping (3 seeds)"
for SEED in 0 1 2; do
    echo "  Seed $SEED..."
    python -u -m src.train --config configs/reward_shaping.yaml --seed $SEED \
        --experiment_name "reward_shaping"
done

# 3. Ablation: Gamma = 0.9
echo ">>> [3/6] Ablation: Gamma = 0.9"
python -u -m src.train --config configs/ablation_gamma.yaml --seed 0 \
    --gamma 0.9 --experiment_name "ablation_gamma0.9"

# 4. Ablation: Gamma = 0.99 (same as reward_shaping seed 0, skip if exists)
echo ">>> [4/6] Ablation: Gamma = 0.99 (reference = reward_shaping_seed0)"

# 5. Ablation: Gamma = 0.999
echo ">>> [5/6] Ablation: Gamma = 0.999"
python -u -m src.train --config configs/ablation_gamma.yaml --seed 0 \
    --gamma 0.999 --experiment_name "ablation_gamma0.999"

# 6. Ablation: No Target Network
echo ">>> [6/6] Ablation: No Target Network"
python -u -m src.train --config configs/ablation_no_target.yaml --seed 0 \
    --experiment_name "ablation_no_target"

echo ""
echo "=========================================="
echo "  All training complete!"
echo "=========================================="
echo "Results saved in: $PROJECT_ROOT/results/"
echo ""
echo "Next steps:"
echo "  1. Run: bash scripts/evaluate_all.sh"
echo "  2. Run: bash scripts/generate_report.sh"
