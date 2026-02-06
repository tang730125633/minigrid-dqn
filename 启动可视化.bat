@echo off
echo ==========================================
echo   MiniGrid DQN 可视化控制台
echo ==========================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
streamlit run app.py
pause
