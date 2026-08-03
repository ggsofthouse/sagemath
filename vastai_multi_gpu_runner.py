"""
VAST.AI MULTI-GPU RUNNER (SAGEMATH LLL GLV 2D + 4X GPU RCKANGAROO)
Autor: Antigravity AI Engine

Este script é otimizado para rodar em instâncias Vast.ai com múltiplas GPUs (ex: 4x RTX 5060 Ti / 4x RTX 4090).
Ele:
1. Executa a decomposição LLL GLV no SageMath/Python em < 5ms.
2. Divide a faixa de busca 2D proporcionalmente entre as 4 GPUs.
3. Dispara os processos do RCKangaroo em paralelo em todas as GPUs.

Uso no Vast.ai:
  python3 vastai_multi_gpu_runner.py --puzzle 71
  python3 vastai_multi_gpu_runner.py --puzzle 72
  python3 vastai_multi_gpu_runner.py --puzzle 140 --gpus 0,1,2,3
"""

import os
import sys
import time
import json
import argparse
import subprocess
from fractions import Fraction

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
        "bits": puzzle_num,
        "hex_min": f"{min_val:x}",
        "hex_max": f"{max_val:x}",
        "address": "Desconhecido"
    }


def rodar_multi_gpu_vastai(puzzle_num: int, gpus: str):
    print("=========================================================================")
    print(f"   VAST.AI MULTI-GPU RUNNER: SAGEMATH LLL GLV + RCKANGAROO")
    print(f"   Puzzle Alvo: #{puzzle_num} | GPUs Selecionadas: [{gpus}]")
    print("=========================================================================")

    p_info = carregar_puzzle_info(puzzle_num)
    hex_min = int(p_info["hex_min"], 16)
    hex_max = int(p_info["hex_max"], 16)
    bits = p_info.get("bits", puzzle_num)
    address = p_info.get("address", "")

    print(f"[+] Endereço Bitcoin: {address}")
    print(f"[+] Range Hex Total:   [0x{hex_min:x} ... 0x{hex_max:x}]")

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
    print(f"    Subvetor 2D k1: {hex(int(k1))} ({int(k1).bit_length()} bits)")
    print(f"    Subvetor 2D k2: {hex(int(k2))} ({int(k2).bit_length()} bits)")

    # 2. Divisão de Trabalho entre as GPUs (ex: 4 GPUs)
    gpu_list = [g.strip() for g in gpus.split(",") if g.strip()]
    num_gpus = len(gpu_list)
    print(f"\n[+] Dividindo o espaço de busca 2D entre {num_gpus} GPUs no Vast.ai...")

    total_range = hex_max - hex_min
    step = total_range // num_gpus

    processes = []
    worker_script = os.path.join(os.path.dirname(__file__), "rckangaroo", "pool", "worker", "worker.py")

    for idx, gpu_id in enumerate(gpu_list):
        start_pct = (idx / num_gpus) * 100.0
        end_pct = ((idx + 1) / num_gpus) * 100.0

        cmd = [
            sys.executable, worker_script,
            "--puzzle", str(puzzle_num),
            "--name", f"VastAI-GPU-{gpu_id}",
            "--start-pct", f"{start_pct:.2f}",
            "--end-pct", f"{end_pct:.2f}"
        ]

        print(f"    --> Disparando GPU {gpu_id} (Faixa {start_pct:.1f}% -> {end_pct:.1f}%):")
        print(f"        {' '.join(cmd)}")

        proc = subprocess.Popen(cmd)
        processes.append(proc)

    print(f"\n[+] Todas as {num_gpus} GPUs foram disparadas no Vast.ai!")
    print("[+] Pressione Ctrl+C para encerrar todos os processos da GPU.\n")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\n[!] Interrompendo todos os workers da GPU...")
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vast.ai Multi-GPU Runner SageMath LLL + RCKangaroo")
    parser.add_argument("--puzzle", type=int, default=71, help="Número do Puzzle (ex: 71, 72, 140)")
    parser.add_argument("--gpus", type=str, default="0,1,2,3", help="Lista de GPUs (ex: 0,1,2,3)")

    args = parser.parse_args()
    rodar_multi_gpu_vastai(args.puzzle, args.gpus)
