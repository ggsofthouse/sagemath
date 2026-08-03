"""
Script de Execução Direta GPU para o Bitcoin Puzzle #72 (100% Standalone Local)
Autor: Antigravity AI Engine

Este script executa o RCKangaroo CUDA Kernel diretamente na GPU para o Puzzle #72 (72 bits)
com DP=14 e estatísticas em GKeys/s, sem qualquer dependência de pool externa.
"""

import os
import sys
import subprocess

PUZZLE_72_ADDR = "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR"
PUZZLE_72_MIN_HEX = "800000000000000000"
PUZZLE_72_MAX_HEX = "ffffffffffffffffff"


def rodar_puzzle_72_gpu_direto(gpus: str = "0,1,2,3", dp_bits: int = 14):
    print("=========================================================================")
    print("   DISPARANDO RCKANGAROO GPU DIRETO NO BITCOIN PUZZLE #72 (72 BITS)")
    print("=========================================================================")
    print(f"[+] Endereço Alvo: {PUZZLE_72_ADDR}")
    print(f"[+] Range Hex Min: 0x{PUZZLE_72_MIN_HEX}")
    print(f"[+] Range Hex Max: 0x{PUZZLE_72_MAX_HEX}")
    print(f"[+] DP Bits:       {dp_bits} | GPUs: [{gpus}]")

    runner_script = os.path.join(os.path.dirname(__file__), "vastai_multi_gpu_runner.py")
    cmd = [
        sys.executable, runner_script,
        "--puzzle", "72",
        "--gpus", gpus,
        "--dp", str(dp_bits)
    ]

    print(f"[+] Executando: {' '.join(cmd)}")
    subprocess.run(cmd)


if __name__ == "__main__":
    rodar_puzzle_72_gpu_direto()
