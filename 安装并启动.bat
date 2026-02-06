@echo off
echo ==========================================
echo   MiniGrid DQN 安装程序
echo ==========================================
cd /d "%~dp0"

:: 检查Python
echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 创建虚拟环境
echo [2/3] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
)

:: 安装依赖
echo [3/3] 安装依赖包...
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install streamlit

echo ==========================================
echo   安装完成！正在启动...
echo ==========================================
timeout /t 2
streamlit run app.py
