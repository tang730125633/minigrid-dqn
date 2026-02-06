#!/bin/bash
echo "=========================================="
echo "  MiniGrid DQN 可视化控制台"
echo "=========================================="
cd "$(dirname "$0")"
source venv/bin/activate
streamlit run app.py
