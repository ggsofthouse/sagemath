# RCKangaroo Standalone Local Worker Script (PowerShell)
$Host.UI.RawUI.WindowTitle = "RCKangaroo Standalone Runner - Local"
Clear-Host

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🦘 RCKangaroo Worker Local (100% Standalone - Sem Pool External)" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$PuzzleNum = Read-Host "👉 Digite o numero do Puzzle (ex: 71, 72, 140) [71]"
if ([string]::IsNullOrWhiteSpace($PuzzleNum)) { $PuzzleNum = "71" }

$DPBits = Read-Host "👉 Valor de DP Bits (padrao 14) [14]"
if ([string]::IsNullOrWhiteSpace($DPBits)) { $DPBits = "14" }

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🚀 Iniciando Runner GPU Local..." -ForegroundColor Yellow
Write-Host "Puzzle:  #$PuzzleNum" -ForegroundColor White
Write-Host "DP Bits: $DPBits" -ForegroundColor White
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$ScriptDir\.."

python vastai_multi_gpu_runner.py --puzzle $PuzzleNum --gpus 0 --dp $DPBits

Read-Host "Pressione ENTER para sair..."
