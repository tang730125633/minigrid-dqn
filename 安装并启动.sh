#!/bin/bash

echo "=========================================="
echo "  MiniGrid DQN 安装程序"
echo "=========================================="
cd "$(dirname "$0")"

# 检查Python
echo "[1/3] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 创建虚拟环境
echo "[2/3] 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 安装依赖
echo "[3/3] 安装依赖包..."
source venv/bin/activate
pip install -r requirements.txt
pip install streamlit

echo "=========================================="
echo "  安装完成！正在启动..."
echo "=========================================="
sleep 2
streamlit run app.py
