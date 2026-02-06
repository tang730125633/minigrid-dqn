#!/bin/bash
# Evaluate all trained models

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  MiniGrid DQN - Evaluate All Models"
echo "=========================================="

python -m src.evaluate --results_dir results --num_episodes 100 --record

echo ""
echo "Evaluation complete!"
echo "Results: results/evaluation_summary.csv"
