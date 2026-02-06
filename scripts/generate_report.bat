@echo off
REM Generate all visualizations and reports

cd /d "%~dp0\.."

echo ==========================================
echo   MiniGrid DQN - Generate Report
echo ==========================================

python -m src.visualize --results_dir results --figures_dir figures --gifs_dir gifs
if errorlevel 1 (
    echo ERROR: Report generation failed!
    exit /b 1
)

echo.
echo Report generated!
echo Figures: figures\
echo GIFs:    gifs\
