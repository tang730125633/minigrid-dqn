# MiniGrid DQN | 强化学习可视化平台

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

一个基于 Deep Q-Network (DQN) 的强化学习项目，带有完整的 Web 可视化界面。

## 🚀 快速开始（无需编程）

### Windows 用户

1. **下载项目**
   - 点击绿色 `<> Code` 按钮 → `Download ZIP`
   - 解压到桌面（或任意位置）

2. **安装 Python**（如未安装）
   - 访问 https://www.python.org/downloads/
   - 下载 Python 3.11 或更高版本
   - **安装时勾选 "Add Python to PATH"** ⚠️

3. **运行程序**
   - 双击 `START.bat`
   - 等待自动安装（首次约 3-5 分钟）
   - 浏览器自动打开 http://localhost:8501

### macOS / Linux 用户

```bash
# 1. 克隆项目
git clone <repository-url>
cd minigrid-dqn

# 2. 运行启动脚本
bash START.sh
```

## 📊 功能特性

- ✅ **开箱即用** - 包含预训练模型和完整实验数据
- ✅ **可视化界面** - Streamlit Web 应用，无需编写代码
- ✅ **实时对比** - DQN vs Reward Shaping 算法性能对比
- ✅ **动画演示** - 观看智能体学习过程的 GIF 动画
- ✅ **一键实验** - 在界面中选择配置即可运行新实验

## 📁 项目结构

```
minigrid-dqn/
├── START.bat              # Windows 启动脚本 ⭐
├── START.sh               # macOS/Linux 启动脚本
├── app.py                 # Web 界面主程序
├── requirements.txt       # Python 依赖
│
├── configs/               # 实验配置文件
│   ├── default.yaml       # Baseline DQN
│   └── reward_shaping.yaml # DQN + Reward Shaping
│
├── src/                   # 源代码
├── results/               # 训练结果 ⭐（已包含）
├── figures/               # 可视化图表 ⭐（已包含）
└── gifs/                  # 动画演示 ⭐（已包含）
```

## 🔬 实验结果预览

项目已包含完整实验数据：

| 方法 | 成功率 | 说明 |
|------|--------|------|
| Baseline DQN | 66.7% ± 47.1% | 标准 DQN |
| **DQN + Reward Shaping** | **100%** | **改进算法** |

无需训练即可查看结果！

## ⚠️ 常见问题

### Q1: 双击 START.bat 闪退？
**解决**: 先安装 Python，并确保安装时勾选 "Add Python to PATH"

### Q2: 提示 "pip 不是内部命令"？
**解决**: Python 安装时未添加到 PATH，建议重新安装 Python

### Q3: 浏览器没有自动打开？
**解决**: 手动访问 http://localhost:8501

### Q4: 安装依赖很慢？
**解决**: 可以切换 pip 镜像源（可选）
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 🛠️ 开发者说明

如需修改代码或重新训练：

```bash
# 创建虚拟环境
python -m venv venv

# 激活环境（Windows）
venv\Scripts\activate

# 激活环境（macOS/Linux）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行训练
python -m src.train --config configs/default.yaml
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**Star ⭐ 如果这个项目对你有帮助！**
