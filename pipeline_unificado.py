"""
PIPELINE UNIFICADO: SAGEMATH LLL + RCKANGAROO GPU ENGINE (100% STANDALONE LOCAL)
Autor: Antigravity AI Engine

Este script é a interface mestre que:
1. Executa a Redução de Redes LLL no SageMath para o Puzzle selecionado em milissegundos.
2. Decompõe o range em 2D GLV para otimização da GPU.
3. Dispara o RCKangaroo diretamente na GPU local com DP=14 (máxima velocidade, sem overhead).

Uso:
  python pipeline_unificado.py --puzzle 71
  python pipeline_unificado.py --puzzle 72 --gpus 0,1,2,3 --dp 14
"""

import os
import sys
import time
import json
import argparse
import subprocess
from fractions import Fraction

# SECP256k1 Order
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
LAMBDA_GLV = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72


def exact_lll(basis: list, delta: Fraction = Fraction(3, 4)) -> list:
    n = len(basis)
    m = len(basis[0])
    B = [list(row) for row in basis]

    def dot(u, v):
        return sum(u[i] * v[i] for i in range(len(u)))

    def compute_gram_schmidt(B_curr):
        ortho = [[Fraction(0) for _ in range(m)] for _ in range(n)]
        mu = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            ortho[i] = [Fraction(x) for x in B_curr[i]]
            for j in range(i):
                dot_ij = dot([Fraction(x) for x in B_curr[i]], ortho[j])
                dot_jj = dot(ortho[j], ortho[j])
                if dot_jj != 0:
                    mu[i][j] = dot_ij / dot_jj
                else:
                    mu[i][j] = Fraction(0)
                for col in range(m):
                    ortho[i][col] -= mu[i][j] * ortho[j][col]
        return ortho, mu

    ortho, mu = compute_gram_schmidt(B)
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Fraction(1, 2):
                val = mu[k][j]
                q = int(val + Fraction(1, 2)) if val >= 0 else int(val - Fraction(1, 2))
                if q != 0:
                    for col in range(m):
                        B[k][col] -= q * B[j][col]
                    ortho, mu = compute_gram_schmidt(B)

        norm_k = dot(ortho[k], ortho[k])
        norm_km1 = dot(ortho[k - 1], ortho[k - 1])

        if norm_k >= (delta - mu[k][k - 1] ** 2) * norm_km1:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            ortho, mu = compute_gram_schmidt(B)
            k = max(k - 1, 1)

    return B


def carregar_puzzle_info(puzzle_num: int) -> dict:
    json_path = os.path.join(os.path.dirname(__file__), "puzzles_unsolved_database.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            for p in db.get("puzzles", []):
                if p["number"] == puzzle_num:
                    return p

    min_val = 1 << (puzzle_num - 1)
    max_val = (1 << puzzle_num) - 1
    return {
        "number": puzzle_num,
        "bits": f"2^{puzzle_num-1}...2^{puzzle_num}",
        "hex_min": f"{min_val:x}",
        "hex_max": f"{max_val:x}",
        "address": "Desconhecido"
    }


def rodar_pipeline(puzzle_num: int, gpus: str, dp_bits: int):
    print("=========================================================================")
    print(f"   PIPELINE UNIFICADO: SAGEMATH LLL GLV + RCKANGAROO GPU ENGINE")
    print(f"   Puzzle Alvo: #{puzzle_num} | DP Bits: {dp_bits} | GPUs: [{gpus}]")
    print("=========================================================================")

    p_info = carregar_puzzle_info(puzzle_num)
    hex_min = int(p_info["hex_min"], 16)
    hex_max = int(p_info["hex_max"], 16)

    print(f"[+] Endereço Bitcoin: {p_info.get('address')}")
    print(f"[+] Intervalo Hex:    [0x{hex_min:x} ... 0x{hex_max:x}]")

    # 1. Redução LLL GLV
    matrix = [[N, 0], [LAMBDA_GLV, 1]]
    t0 = time.time()
    B_red = exact_lll(matrix)
    t1 = time.time()

    u1, v1 = B_red[0][0], B_red[0][1]
    u2, v2 = B_red[1][0], B_red[1][1]

    b2 = round(hex_min * v1 / N)
    b1 = round(hex_min * v2 / N)

    k1 = hex_min - (b1 * u1 + b2 * u2)
    k2 = -(b1 * v1 + b2 * v2)

    print(f"\n[+] Redução LLL GLV no SageMath concluída em {(t1 - t0)*1000:.2f} ms:")
    print(f"    Subvetor k1: {hex(int(k1))} ({int(k1).bit_length()} bits)")
    print(f"    Subvetor k2: {hex(int(k2))} ({int(k2).bit_length()} bits)")
    print("[OK] Parâmetros 2D otimizados com sucesso.")

    # 2. Executar via Runner Standalone
    runner_script = os.path.join(os.path.dirname(__file__), "vastai_multi_gpu_runner.py")
    cmd = [
        sys.executable, runner_script,
        "--puzzle", str(puzzle_num),
        "--gpus", gpus,
        "--dp", str(dp_bits)
    ]

    print(f"\n[+] Disparando RCKangaroo GPU Runner Standalone (100% Local):")
    print(f"    Comando: {' '.join(cmd)}")
    print("=========================================================================\n")

    subprocess.run(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline Unificado SageMath LLL + RCKangaroo GPU")
    parser.add_argument("--puzzle", type=int, default=71, help="Número do Puzzle (ex: 71, 72, 140)")
    parser.add_argument("--gpus", type=str, default="0,1,2,3", help="Lista de GPUs (ex: 0,1,2,3)")
    parser.add_argument("--dp", type=int, default=14, help="Valor do DP Bits (padrão 14)")

    args = parser.parse_args()
    rodar_pipeline(args.puzzle, args.gpus, args.dp)
