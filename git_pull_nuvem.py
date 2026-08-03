"""
SCRIPT DE ATUALIZAÇÃO GIT PULL E EXECUÇÃO LOCAL NA NUVEM (VAST.AI / LINUX / WINDOWS)
Autor: Antigravity AI Engine

Uso:
  python3 git_pull_nuvem.py --puzzle 71 --gpus 0,1,2,3 --dp 14
"""

import os
import sys
import argparse
import subprocess

def git_pull_and_run(puzzle: int, gpus: str, dp: int):
    print("=========================================================================")
    print("   [GIT PULL] ATUALIZANDO REPOSITÓRIO NA NUVEM E COMPILANDO")
    print("=========================================================================")
    
    # 1. Git pull
    try:
        res = subprocess.run(["git", "pull"], capture_output=True, text=True)
        print(f"[+] Git Pull Output: {res.stdout.strip()}")
    except Exception as e:
        print(f"[!] Erro no git pull: {e}")

    # 2. Executar Runner Standalone
    runner_script = os.path.join(os.path.dirname(__file__), "vastai_multi_gpu_runner.py")
    cmd = [
        sys.executable, runner_script,
        "--puzzle", str(puzzle),
        "--gpus", gpus,
        "--dp", str(dp)
    ]
    print(f"\n[+] Executando Runner Standalone: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Git Pull e Run para Nuvem")
    parser.add_argument("--puzzle", type=int, default=71, help="Número do Puzzle (ex: 71)")
    parser.add_argument("--gpus", type=str, default="0,1,2,3", help="GPUs a usar")
    parser.add_argument("--dp", type=int, default=14, help="Valor DP bits")
    args = parser.parse_args()
    git_pull_and_run(args.puzzle, args.gpus, args.dp)
