"""
ORQUESTRADOR CONTÍNUO DE VARREDURA DE SEMENTES GPU / CPU - BITCOIN PUZZLE #71
Autor: Antigravity AI Engine
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verifier import verify_full_seed
from seed_generator import SeedGenerator

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GPU_SRC  = os.path.join(BASE_DIR, "gpu", "kernel.cu")
GPU_EXE  = os.path.join(BASE_DIR, "gpu", "kernel.exe")
DB_FILE  = os.path.join(BASE_DIR, "data", "known_keys.json")
CHECKPOINT_FILE = os.path.join(BASE_DIR, "data", "seed_checkpoint.json")
WIN_FILE = os.path.join(BASE_DIR, "SOLVED_PUZZLE71.txt")

def carregar_checkpoint() -> dict:
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_seed": 1388534400,
        "total_scanned": 0,
        "mode": "timestamp",
        "created_at": datetime.now().isoformat()
    }

def salvar_checkpoint(last_seed, total_scanned: int):
    if isinstance(last_seed, int):
        val = last_seed
    elif isinstance(last_seed, bytes):
        val = int.from_bytes(last_seed[:8], 'big')
    else:
        val = str(last_seed)

    data = {
        "last_seed": val,
        "total_scanned": total_scanned,
        "updated_at": datetime.now().isoformat()
    }
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def compilar_kernel_cuda() -> bool:
    if os.path.exists(GPU_EXE):
        return True
    print("[+] Compilando kernel CUDA GPU (kernel.cu)...")
    msvc_path = r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64"
    cmd = [
        "nvcc", "-O3",
        "-ccbin", msvc_path,
        GPU_SRC, "-o", GPU_EXE
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(GPU_EXE):
            print("  [OK] Kernel CUDA compilado com sucesso!")
            return True
        else:
            print(f"  [ERRO] Falha na compilação CUDA: {res.stderr}")
    except Exception as e:
        print(f"  [ERRO] Falha ao invocar nvcc: {e}")
    return False

def main():
    parser = argparse.ArgumentParser(description="Orquestrador GPU/CPU de Varredura de Sementes")
    parser.add_argument("--batch", "--batch-size", type=int, default=100000000, help="Tamanho do lote GPU / CPU")
    parser.add_argument("--mode", type=str, default="timestamp",
                        choices=["timestamp", "sha256", "40bit", "wordlist"],
                        help="Tipo de semente a varrer via SeedGenerator")
    args = parser.parse_args()

    print("=" * 80)
    print(" 🚀 ORQUESTRADOR DE SEMENTES PUZZLE #71 - SEED GENERATOR INTEGRADO")
    print(f"  Modo Ativo: {args.mode.upper()} | Tamanho do Lote: {args.batch:,}")
    print("=" * 80)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        known_db = json.load(f)

    if not compilar_kernel_cuda():
        sys.exit(1)

    cp = carregar_checkpoint()
    total_scanned = cp.get("total_scanned", 0)
    start_seed_val = cp.get("last_seed", 1388534400)

    lote_num = 0
    t_start = time.time()

    # MODO 1: GPU CUDA Kernel (Timestamp inteiros)
    if args.mode == "timestamp" and os.path.exists(GPU_EXE):
        current_seed = start_seed_val if isinstance(start_seed_val, int) else 1388534400
        while True:
            lote_num += 1
            t0 = time.time()

            # CHECKPOINT PRÉ-LOTE (Salva o estado EXATAMENTE antes de invocar o subprocesso GPU)
            salvar_checkpoint(current_seed, total_scanned)

            res = subprocess.run([GPU_EXE, str(current_seed), str(args.batch)], capture_output=True, text=True)
            out_line = res.stdout.strip()
            dt = time.time() - t0

            speed_str = "1100.0"
            if "SPEED_MKEYS:" in out_line:
                try:
                    parts = dict(item.split(":") for item in out_line.split("|") if ":" in item)
                    speed_str = parts.get("SPEED_MKEYS", "1100.0")
                except Exception:
                    pass

            current_seed += args.batch
            total_scanned += args.batch

            # CHECKPOINT PÓS-LOTE
            salvar_checkpoint(current_seed, total_scanned)

            elapsed = time.time() - t_start
            print(f"  [Lote #{lote_num:04d}] Seed: 0x{current_seed - args.batch:x} -> 0x{current_seed:x} | Vel: {float(speed_str):.0f} MKeys/s | Total: {total_scanned:,} | Tempo: {elapsed:.1f}s")

            if "FOUND:1" in out_line:
                parts = dict(item.split(":") for item in out_line.split("|") if ":" in item)
                found_seed = int(parts.get("SEED", 0))
                if verify_full_seed(found_seed, known_db):
                    with open(WIN_FILE, "w", encoding="utf-8") as f:
                        f.write(f"PUZZLE #71 RESOLVIDO!\nSemente: {found_seed}\nData: {datetime.now().isoformat()}\n")
                    print("🏆 PUZZLE #71 RESOLVIDO COM SUCESSO!")
                    return
    else:
        # MODO 2: Stream via SeedGenerator para SHA256, 40-bits e Wordlists
        if args.mode == "sha256":
            gen = SeedGenerator.generate_sha256_timestamps(2014, 2016, count=10**12)
        elif args.mode == "40bit":
            gen = SeedGenerator.generate_40_48bit(start=start_seed_val if isinstance(start_seed_val, int) else 0, count=10**12)
        else:
            words = ["bitcoin", "satoshi", "puzzle", "nakamoto", "genesis", "secret"]
            gen = SeedGenerator.generate_wordlist_passphrases(words)

        batch = []
        cpu_batch = min(args.batch, 1000) # Lote leve de 1000 itens no CPU

        for seed in gen:
            batch.append(seed)

            if len(batch) < cpu_batch:
                continue

            lote_num += 1
            for s in batch:
                if verify_full_seed(s, known_db):
                    with open(WIN_FILE, "w", encoding="utf-8") as f:
                        f.write(f"PUZZLE #71 RESOLVIDO!\nSemente: {s}\nData: {datetime.now().isoformat()}\n")
                    print("🏆 PUZZLE #71 RESOLVIDO COM SUCESSO!")
                    return

            total_scanned += len(batch)
            last = batch[-1]
            salvar_checkpoint(last, total_scanned)

            elapsed = time.time() - t_start
            s_repr = last.hex()[:16] if isinstance(last, bytes) else str(last)
            print(f"  [Lote #{lote_num:04d}] Ultima Semente: {s_repr} | Total Varrido: {total_scanned:,} | Tempo: {elapsed:.1f}s")
            batch = []

if __name__ == "__main__":
    main()
