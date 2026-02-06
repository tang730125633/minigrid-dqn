#!/bin/bash
# Generate all visualizations and reports

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "  MiniGrid DQN - Generate Report"
echo "=========================================="

python -m src.visualize --results_dir results --figures_dir figures --gifs_dir gifs

echo ""
echo "Report generated!"
echo "Figures: figures/"
echo "GIFs:    gifs/"
