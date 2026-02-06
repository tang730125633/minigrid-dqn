@echo off
REM Evaluate all trained models

cd /d "%~dp0\.."

echo ==========================================
echo   MiniGrid DQN - Evaluate All Models
echo ==========================================

python -m src.evaluate --results_dir results --num_episodes 100 --record
if errorlevel 1 (
    echo ERROR: Evaluation failed!
    exit /b 1
)

echo.
echo Evaluation complete!
echo Results: results\evaluation_summary.csv
