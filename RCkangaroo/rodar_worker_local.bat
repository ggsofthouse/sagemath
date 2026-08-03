@echo off
title RCKangaroo Standalone Runner - Maquina Local
cls
echo ==================================================
echo 🦘 RCKangaroo Worker Local (100%% Standalone - Sem Pool External)
echo ==================================================
echo.

set /p PUZZLE_NUM="👉 Digite o numero do Puzzle (ex: 71, 72, 140) [71]: "
if "%PUZZLE_NUM%"=="" set PUZZLE_NUM=71

set /p DP_BITS="👉 Valor de DP Bits (padrao 14) [14]: "
if "%DP_BITS%"=="" set DP_BITS=14

echo.
echo ==================================================
echo 🚀 Iniciando Runner GPU Local...
echo Puzzle:  #%PUZZLE_NUM%
echo DP Bits: %DP_BITS%
echo ==================================================
echo.

cd /d "%~dp0\.."
python vastai_multi_gpu_runner.py --puzzle %PUZZLE_NUM% --gpus 0 --dp %DP_BITS%

pause
