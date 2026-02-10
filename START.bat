@echo off
chcp 65001 >nul
echo ==========================================
echo   MiniGrid DQN 可视化平台
echo ==========================================
echo.

:: 切换到脚本所在目录（处理中文路径）
cd /d "%~dp0"
echo [INFO] 工作目录: %CD%
echo.

:: 检查Python
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！
    echo.
    echo 请安装 Python 3.8 或更高版本：
    echo https://www.python.org/downloads/
    echo.
    echo 安装时请务必勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python --version
echo.

:: 创建虚拟环境
echo [2/4] 检查虚拟环境...
if not exist "venv" (
    echo [INFO] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
) else (
    echo [INFO] 虚拟环境已存在
)
echo.

:: 激活环境并安装依赖
echo [3/4] 检查依赖包...
call venv\Scripts\activate.bat

:: 检查是否需要安装依赖
if not exist "venv\Lib\site-packages\streamlit" (
    echo [INFO] 首次安装依赖，请稍候...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 安装依赖失败
        pause
        exit /b 1
    )
) else (
    echo [INFO] 依赖已安装
)
echo.

:: 检查数据文件
echo [4/4] 检查数据文件...
if not exist "results\evaluation_summary.csv" (
    echo [警告] 未找到实验结果数据
    echo [INFO] 程序将使用示例数据运行
) else (
    echo [INFO] 找到实验结果: %CD%\results
)
echo.

:: 启动应用
echo ==========================================
echo   正在启动可视化界面...
echo ==========================================
echo.
echo 启动后会自动打开浏览器
echo 如果没有自动打开，请手动访问: http://localhost:8501
echo.
timeout /t 3 >nul

streamlit run app.py --server.port 8501

:: 如果streamlit退出，暂停显示错误
if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    pause
)
