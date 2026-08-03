@echo off
title RCKangaroo Pool Worker - Maquina Local (RTX 2060 SUPER)
cls
echo ==================================================
echo 🦘 RCKangaroo Worker Local - Conexao Pool
echo Servidor: https://valyrafi.com.br
echo ==================================================
echo.

set /p PUZZLE_NUM="👉 Digite o numero do Puzzle (ex: 140) [140]: "
if "%PUZZLE_NUM%"=="" set PUZZLE_NUM=140

set /p START_PCT="👉 Porcentagem INICIAL do range (0 a 100) [85.0]: "
if "%START_PCT%"=="" set START_PCT=85.0

set /p END_PCT="👉 Porcentagem FINAL do range (0 a 100) [100.0]: "
if "%END_PCT%"=="" set END_PCT=100.0

echo.
echo ==================================================
echo 🚀 Iniciando Worker Local...
echo Puzzle:  #%PUZZLE_NUM%
echo Range:   %START_PCT%%% ate %END_PCT%%%
echo ==================================================
echo.

cd /d "%~dp0"
python pool/worker/worker.py --server https://valyrafi.com.br --name "Local-RTX2060" --puzzle %PUZZLE_NUM% --start-pct %START_PCT% --end-pct %END_PCT% --non-interactive

pause
