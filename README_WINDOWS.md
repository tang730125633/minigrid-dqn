# Windows 用户快速开始指南

## 第一步：下载项目

1. 点击 GitHub 页面上的 **绿色 "Code" 按钮**
2. 选择 **"Download ZIP"**
3. 解压到桌面，得到文件夹 `minigrid-dqn_副本`

## 第二步：安装 Python（如果还没有）

1. 访问 https://www.python.org/downloads/
2. 下载 **Python 3.11**（推荐）
3. **重要**：安装时勾选 **"Add Python to PATH"**
   ![Add to PATH](https://docs.python.org/3/_images/win_installer.png)

## 第三步：运行项目

### 方法：双击启动（最简单）

1. 打开解压后的文件夹
2. **双击 `安装并启动.bat`**
3. 等待安装完成（首次约 3-5 分钟）
4. 浏览器自动打开 http://localhost:8501

### 如果双击无法运行

打开命令提示符 (CMD)，执行：

```cmd
cd Desktop\minigrid-dqn_副本
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 常见问题

### Q: 提示 "python 不是内部或外部命令"
**解决**：Python 没有添加到 PATH，重新安装 Python 并勾选 "Add to PATH"

### Q: 安装很慢或卡住
**解决**：这是正常的，PyTorch 比较大。可以更换国内镜像源：

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 浏览器没有自动打开
**解决**：手动访问 http://localhost:8501

### Q: 提示 "ModuleNotFoundError"
**解决**：依赖没有安装完整，重新运行 `安装并启动.bat`

## 项目结构

```
minigrid-dqn_副本/
├── app.py                 ← Web界面
├── 安装并启动.bat         ← Windows启动脚本 ⭐
├── configs/               ← 实验配置
├── src/                   ← 源代码
├── results/               ← 训练好的模型
├── figures/               ← 可视化图表
└── gifs/                  ← 动画演示
```

## 快速体验

启动后，点击 **"查看最新结果"** 即可查看：
- ✅ 训练曲线对比
- ✅ 成功率柱状图
- ✅ 消融实验结果
- ✅ GIF 动画演示

无需等待训练，立即可见结果！

## 需要帮助？

联系项目作者或提交 GitHub Issue。
