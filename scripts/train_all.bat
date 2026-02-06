@echo off
REM Train all experiments: baseline, reward shaping, and ablation studies
cd /d "%~dp0\.."

echo ==========================================
echo   MiniGrid DQN - Train All Experiments
echo ==========================================
echo Project root: %CD%
echo.

REM 1. Baseline DQN (3 seeds)
echo [1/6] Baseline DQN (3 seeds)
for %%S in (0 1 2) do (
    echo   Seed %%S...
    python -u -m src.train --config configs/default.yaml --seed %%S --experiment_name "baseline"
    if errorlevel 1 goto :error
)

REM 2. DQN + Reward Shaping (3 seeds)
echo [2/6] DQN + Reward Shaping (3 seeds)
for %%S in (0 1 2) do (
    echo   Seed %%S...
    python -u -m src.train --config configs/reward_shaping.yaml --seed %%S --experiment_name "reward_shaping"
    if errorlevel 1 goto :error
)

REM 3. Ablation: Gamma = 0.9
echo [3/6] Ablation: Gamma = 0.9
python -u -m src.train --config configs/ablation_gamma.yaml --seed 0 --gamma 0.9 --experiment_name "ablation_gamma0.9"
if errorlevel 1 goto :error

REM 4. Ablation: Gamma = 0.99 (reference = reward_shaping_seed0)
echo [4/6] Ablation: Gamma = 0.99 (reference = reward_shaping_seed0)

REM 5. Ablation: Gamma = 0.999
echo [5/6] Ablation: Gamma = 0.999
python -u -m src.train --config configs/ablation_gamma.yaml --seed 0 --gamma 0.999 --experiment_name "ablation_gamma0.999"
if errorlevel 1 goto :error

REM 6. Ablation: No Target Network
echo [6/6] Ablation: No Target Network
python -u -m src.train --config configs/ablation_no_target.yaml --seed 0 --experiment_name "ablation_no_target"
if errorlevel 1 goto :error

echo.
echo ==========================================
echo   All training complete!
echo ==========================================
echo Results saved in: %CD%\results\
echo.
echo Next steps:
echo   1. Run: scripts\evaluate_all.bat
echo   2. Run: scripts\generate_report.bat
goto :eof

:error
echo.
echo ERROR: Training failed! Check the output above.
exit /b 1
