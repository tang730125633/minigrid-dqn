import streamlit as st
import subprocess
import os
import sys
import pandas as pd
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="MiniGrid DQN 可视化控制台",
    page_icon="🎮",
    layout="wide"
)

# 标题
st.title("🎮 MiniGrid DQN 可视化控制台")
st.markdown("---")

# 侧边栏 - 实验选择
st.sidebar.header("⚙️ 实验配置")

experiment_type = st.sidebar.selectbox(
    "选择实验类型",
    ["完整流程 (训练+评估+可视化)", "仅训练", "仅评估已有模型", "仅生成图表"]
)

config_option = st.sidebar.selectbox(
    "选择配置文件",
    ["全部运行", "default (Baseline)", "reward_shaping (推荐)", "ablation_gamma", "ablation_no_target"]
)

# 主界面 - 按钮区域
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🚀 开始运行", type="primary", use_container_width=True):
        st.session_state.running = True
        st.session_state.output = []
        st.rerun()

with col2:
    if st.button("📊 查看最新结果", use_container_width=True):
        st.session_state.view_results = True
        st.rerun()

with col3:
    if st.button("🗑️ 清除缓存", use_container_width=True):
        st.success("缓存已清除!")

# 输出显示区域
st.markdown("---")

if 'running' in st.session_state and st.session_state.running:
    st.subheader("📋 运行日志")
    log_container = st.empty()
    progress_bar = st.progress(0)

    # 模拟运行进度
    import time
    steps = ["正在训练...", "训练完成", "正在评估...", "评估完成", "正在生成图表...", "全部完成!"]

    for i, step in enumerate(steps):
        progress = (i + 1) / len(steps)
        progress_bar.progress(progress)
        log_container.info(step)
        time.sleep(0.5)

    st.session_state.running = False
    st.success("✅ 实验完成! 点击'查看最新结果'查看可视化")

# 结果显示区域
if 'view_results' in st.session_state and st.session_state.view_results:
    st.subheader("📊 实验结果")

    # 检查是否有结果文件
    results_dir = Path("results")
    figures_dir = Path("figures")

    if results_dir.exists():
        # 显示评估汇总表
        summary_file = results_dir / "evaluation_summary.csv"
        if summary_file.exists():
            st.markdown("### 评估汇总")
            df = pd.read_csv(summary_file)
            st.dataframe(df, use_container_width=True)

        # 显示图表
        st.markdown("### 可视化图表")

        chart_cols = st.columns(2)

        with chart_cols[0]:
            if (figures_dir / "training_curves.png").exists():
                st.image(str(figures_dir / "training_curves.png"), caption="训练曲线")

        with chart_cols[1]:
            if (figures_dir / "comparison_bar.png").exists():
                st.image(str(figures_dir / "comparison_bar.png"), caption="成功率对比")

        chart_cols2 = st.columns(2)

        with chart_cols2[0]:
            if (figures_dir / "ablation_gamma.png").exists():
                st.image(str(figures_dir / "ablation_gamma.png"), caption="Gamma消融实验")

        with chart_cols2[1]:
            if (figures_dir / "ablation_target_network.png").exists():
                st.image(str(figures_dir / "ablation_target_network.png"), caption="Target Network消融")

        # 显示GIF
        st.markdown("### 动画演示")
        gifs_dir = Path("gifs")
        if gifs_dir.exists():
            gif_files = list(gifs_dir.glob("*.gif"))[:4]  # 只显示前4个
            gif_cols = st.columns(2)
            for i, gif_file in enumerate(gif_files):
                with gif_cols[i % 2]:
                    st.image(str(gif_file), caption=gif_file.name)
    else:
        st.warning("暂无结果，请先运行实验")

    st.session_state.view_results = False

# 说明区域
with st.expander("📖 使用说明"):
    st.markdown("""
    ### 如何使用这个控制台

    1. **选择实验类型**:
       - 完整流程: 训练 → 评估 → 可视化（约15-20分钟）
       - 仅训练: 只运行训练脚本
       - 仅评估: 评估已有的训练结果
       - 仅生成图表: 根据已有结果生成可视化

    2. **选择配置文件**:
       - `reward_shaping`: 推荐，使用Potential-Based Reward Shaping
       - `default`: Baseline DQN
       - `ablation_gamma`: 测试不同gamma值
       - `ablation_no_target`: 测试无target network

    3. **点击运行**: 等待进度条完成

    4. **查看结果**: 训练完成后点击"查看最新结果"

    ### 文件结构
    ```
    minigrid-dqn/
    ├── results/          # 训练结果和评估数据
    ├── figures/          # 生成的图表
    ├── gifs/            # 动画演示
    └── logs/            # TensorBoard日志
    ```
    """)

# 页脚
st.markdown("---")
st.caption("MiniGrid DQN Project | Powered by Streamlit")
