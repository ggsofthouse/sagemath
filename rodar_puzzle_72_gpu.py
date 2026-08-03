"""
Script de Execução Direta GPU para o Bitcoin Puzzle #72
Autor: Antigravity AI Engine

Este script ignora a fila do servidor pool e executa o RCKangaroo CUDA Kernel
diretamente na GPU para o Puzzle #72 (72 bits) com os parâmetros do SageMath LLL.
"""

import os
import sys
import subprocess

PUZZLE_72_ADDR = "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR"
PUZZLE_72_MIN_HEX = "800000000000000000"
PUZZLE_72_MAX_HEX = "ffffffffffffffffff"


def rodar_puzzle_72_gpu_direto():
    print("=========================================================================")
    print("   DISPARANDO RCKANGAROO GPU DIRETO NO BITCOIN PUZZLE #72 (72 BITS)")
    print("=========================================================================")
    print(f"[+] Endereço Alvo: {PUZZLE_72_ADDR}")
    print(f"[+] Range Hex Min: 0x{PUZZLE_72_MIN_HEX}")
    print(f"[+] Range Hex Max: 0x{PUZZLE_72_MAX_HEX}")

    rckangaroo_dir = os.path.join(os.path.dirname(__file__), "rckangaroo")
    exe_path = os.path.join(rckangaroo_dir, "x64", "Release", "RCKangaroo.exe")

    if not os.path.exists(exe_path):
        print(f"[-] Executável {exe_path} não encontrado. Usando worker python...")
        cmd = [
            sys.executable,
            os.path.join(rckangaroo_dir, "pool", "worker", "worker.py"),
            "--puzzle", "72",
            "--name", "Local-RTX2060-Puzzle72"
        ]
    else:
        cmd = [
            exe_path,
            "-gpu", "0",
            "-dp", "18",
            "-range", "72",
            "-start", PUZZLE_72_MIN_HEX,
            "-keyspace", PUZZLE_72_MAX_HEX,
            "-addr", PUZZLE_72_ADDR
        ]

    print(f"[+] Executando: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=rckangaroo_dir)


if __name__ == "__main__":
    rodar_puzzle_72_gpu_direto()
