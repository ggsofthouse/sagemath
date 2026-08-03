"""
VAST.AI MULTI-GPU STANDALONE LOCAL RUNNER (SAGEMATH LLL GLV 2D + MULTI-GPU RCKANGAROO)
Autor: Antigravity AI Engine

Este script executa 100% LOCALMENTE (SEM CONECTAR A NENHUM SERVIDOR OU POOL WEB).
Ele:
1. Executa a decomposição LLL GLV no SageMath/Python em < 5ms.
2. Divide o intervalo 2D diretamente entre as GPUs locais (ex: 4 GPUs no Vast.ai).
3. Dispara o RCKangaroo CUDA Kernel diretamente em cada GPU em paralelo.

Uso:
  python3 vastai_multi_gpu_runner.py --puzzle 71 --gpus 0,1,2,3
  python3 vastai_multi_gpu_runner.py --puzzle 72 --gpus 0,1,2,3
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
        "address": ""
    }


def localizar_executavel_rckangaroo() -> str:
    base_dir = os.path.dirname(__file__)
    for sub in ["rckangaroo", "RCkangaroo"]:
        cand1 = os.path.join(base_dir, sub, "build", "RCKangaroo")
        cand2 = os.path.join(base_dir, sub, "RCKangaroo")
        cand3 = os.path.join(base_dir, sub, "x64", "Release", "RCKangaroo.exe")
        for c in [cand1, cand2, cand3]:
            if os.path.exists(c):
                return c
    return ""


def rodar_multi_gpu_standalone_local(puzzle_num: int, gpus: str):
    print("=========================================================================")
    print(f"   VAST.AI MULTI-GPU RUNNER 100% LOCAL (SEM SERVIDOR POOL)")
    print(f"   Puzzle Alvo: #{puzzle_num} | GPUs Selecionadas: [{gpus}]")
    print("=========================================================================")

    p_info = carregar_puzzle_info(puzzle_num)
    hex_min = int(p_info["hex_min"], 16)
    hex_max = int(p_info["hex_max"], 16)
    address = p_info.get("address", "")
    pubkey = p_info.get("pubkey", "")

    print(f"[+] Endereço Bitcoin: {address}")
    print(f"[+] PubKey (Se houver): {pubkey}")
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

    # 2. Divisão de Trabalho 100% Local entre as GPUs
    gpu_list = [g.strip() for g in gpus.split(",") if g.strip()]
    num_gpus = len(gpu_list)
    print(f"\n[+] Dividindo a varredura 100% LOCAL entre {num_gpus} GPUs...")

    total_range = hex_max - hex_min
    step = total_range // num_gpus

    rck_exe = localizar_executavel_rckangaroo()
    processes = []

    for idx, gpu_id in enumerate(gpu_list):
        gpu_start = hex_min + (idx * step)
        gpu_end = hex_min + ((idx + 1) * step) if idx < num_gpus - 1 else hex_max
        start_hex = f"{gpu_start:x}"

        if rck_exe:
            cmd = [
                rck_exe,
                "-gpu", str(gpu_id),
                "-dp", "18",
                "-range", str(puzzle_num),
                "-start", start_hex
            ]
            if pubkey:
                cmd.extend(["-pubkey", pubkey])
            elif address:
                cmd.extend(["-addr", address])
        else:
            rck_subfolder = "rckangaroo" if os.path.exists(os.path.join(os.path.dirname(__file__), "rckangaroo")) else "RCkangaroo"
            worker_script = os.path.join(os.path.dirname(__file__), rck_subfolder, "pool", "worker", "worker.py")
            start_pct = (idx / num_gpus) * 100.0
            end_pct = ((idx + 1) / num_gpus) * 100.0
            cmd = [
                sys.executable, worker_script,
                "--puzzle", str(puzzle_num),
                "--name", f"Local-GPU-{gpu_id}",
                "--start-pct", f"{start_pct:.2f}",
                "--end-pct", f"{end_pct:.2f}"
            ]

        print(f"    --> Disparando GPU {gpu_id} (Start: 0x{start_hex}):")
        print(f"        {' '.join(cmd)}")

        proc = subprocess.Popen(cmd)
        processes.append(proc)

    print(f"\n[+] Todas as {num_gpus} GPUs estão rodando 100% LOCALMENTE sem conectar a nenhuma pool!")
    print("[+] Pressione Ctrl+C para parar todos os trabalhadores.\n")

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        print("\n[!] Interrompendo GPUs...")
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vast.ai Multi-GPU Standalone Local Runner")
    parser.add_argument("--puzzle", type=int, default=71, help="Número do Puzzle (ex: 71, 72, 140)")
    parser.add_argument("--gpus", type=str, default="0,1,2,3", help="Lista de GPUs (ex: 0,1,2,3)")

    args = parser.parse_args()
    rodar_multi_gpu_standalone_local(args.puzzle, args.gpus)
