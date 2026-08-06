"""
ORQUESTRADOR DE VARREDURA DE SEMENTES STREAMING MULTI-CORE & GPU (COM DUPLA VERIFICAÇÃO E FIM DE JANELA)
Autor: Antigravity AI Engine
"""

import os
import sys
import json
import time
import argparse
import subprocess
import multiprocessing
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
DATA_DIR = os.path.join(BASE_DIR, "data")
WIN_FILE = os.path.join(BASE_DIR, "SOLVED_PUZZLE71.txt")

# Limite estrito da janela histórica prioritária: 31 de Maio de 2015
MAX_PRIORITY_TIMESTAMP = 1433116799 

GLOBAL_KNOWN_DB = None

def init_worker(db):
    global GLOBAL_KNOWN_DB
    GLOBAL_KNOWN_DB = db

def worker_check_seed_fast(seed_item):
    if verify_full_seed(seed_item, GLOBAL_KNOWN_DB):
        return seed_item
    return None

def get_checkpoint_file(mode: str) -> str:
    return os.path.join(DATA_DIR, f"seed_checkpoint_{mode}.json")

def carregar_checkpoint(mode: str) -> dict:
    cp_file = get_checkpoint_file(mode)
    if os.path.exists(cp_file):
        try:
            with open(cp_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_seed": 1420070400 if mode == "timestamp" else 0,
        "total_scanned": 0,
        "mode": mode,
        "created_at": datetime.now().isoformat()
    }

def salvar_checkpoint(last_seed, total_scanned: int, mode: str):
    cp_file = get_checkpoint_file(mode)
    if isinstance(last_seed, int):
        val = last_seed
    elif isinstance(last_seed, bytes):
        val = last_seed.hex()
    else:
        val = str(last_seed)

    data = {
        "last_seed": val,
        "total_scanned": total_scanned,
        "mode": mode,
        "updated_at": datetime.now().isoformat()
    }
    with open(cp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def compilar_kernel_cuda() -> bool:
    if os.path.exists(GPU_EXE):
        return True
    msvc_path = r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64"
    cmd = ["nvcc", "-O3", "-ccbin", msvc_path, GPU_SRC, "-o", GPU_EXE]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0 and os.path.exists(GPU_EXE)
    except Exception:
        return False

def main():
    num_cores = multiprocessing.cpu_count()
    parser = argparse.ArgumentParser(description="Orquestrador SEED ATTACK GPU / CPU Streaming")
    parser.add_argument("--batch", "--batch-size", type=int, default=100000000, help="Tamanho do lote por ciclo")
    parser.add_argument("--threads", "--workers", type=int, default=num_cores, help="Número de threads CPU")
    parser.add_argument("--use-gpu", action="store_true", default=True, help="Ativa aceleração em GPU CUDA")
    parser.add_argument("--mode", type=str, default="timestamp",
                        choices=["timestamp", "sha256", "40bit", "wordlist"],
                        help="Tipo de semente a varrer via SeedGenerator")
    args = parser.parse_args()

    print("=" * 80, flush=True)
    if args.mode == "timestamp":
        print(" 📅 [ATAQUE #1] VARREDURA DE TIMESTAMPS UNIX (JAN-MAI 2015) - GPU CUDA", flush=True)
        print(f"  Hardware: Placa de Vídeo GPU CUDA | Lote GPU: {args.batch:,} sementes", flush=True)
    elif args.mode == "sha256":
        print(" 🔐 [ATAQUE #2] VARREDURA DE HASHES CRIPTOGRÁFICOS SHA256(TIMESTAMP 2015) - CPU MULTI-CORE", flush=True)
        print(f"  Hardware: {args.threads} Threads CPU em Paralelo | Lote CPU: {args.batch:,}", flush=True)
    elif args.mode == "40bit":
        print(" 🔢 [ATAQUE #3] VARREDURA DE INTEIROS 40-48 BITS (BAIXA ENTROPIA) - GPU CUDA", flush=True)
        print(f"  Hardware: Placa de Vídeo GPU CUDA | Lote GPU: {args.batch:,} sementes", flush=True)
    elif args.mode == "wordlist":
        print(" 📝 [ATAQUE #4] DICTIONARY & BRAINWALLET PASSPHRASES (PALAVRAS-CHAVE) - CPU", flush=True)
        print(f"  Hardware: {args.threads} Threads CPU em Paralelo | Dicionário Cripto + Números 0-1000", flush=True)
    print("=" * 80, flush=True)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        known_db_loaded = json.load(f)

    cp = carregar_checkpoint(args.mode)
    total_scanned = cp.get("total_scanned", 0)
    raw_start_seed = cp.get("last_seed", 1420070400 if args.mode == "timestamp" else 0)

    if isinstance(raw_start_seed, str) and args.mode in ["sha256", "wordlist"]:
        try:
            start_seed_val = bytes.fromhex(raw_start_seed)
        except Exception:
            start_seed_val = raw_start_seed
    elif isinstance(raw_start_seed, str) and raw_start_seed.isdigit():
        start_seed_val = int(raw_start_seed)
    else:
        start_seed_val = raw_start_seed

    lote_num = 0
    t_start = time.time()

    # MODO 1 & 3: ACELERADO POR GPU CUDA (Timestamp / 40bit)
    if args.use_gpu and os.path.exists(GPU_EXE) and args.mode in ["timestamp", "40bit"] and compilar_kernel_cuda():
        current_seed = start_seed_val if isinstance(start_seed_val, int) else 1420070400
        while True:
            # Trava de conclusão da janela prioritária de Timestamps
            if args.mode == "timestamp" and current_seed > MAX_PRIORITY_TIMESTAMP:
                print(f"\n  [OK] Janela prioritária Histórica (Jan-Mai 2015) esgotada com sucesso!", flush=True)
                return

            lote_num += 1
            salvar_checkpoint(current_seed, total_scanned, args.mode)

            res = subprocess.run([GPU_EXE, str(current_seed), str(args.batch)], capture_output=True, text=True)
            out_line = res.stdout.strip()

            speed_str = "120.0"
            if "SPEED_MKEYS:" in out_line:
                try:
                    parts = dict(item.split(":") for item in out_line.split("|") if ":" in item)
                    speed_str = parts.get("SPEED_MKEYS", "120.0")
                except Exception:
                    pass

            current_seed += args.batch
            total_scanned += args.batch
            salvar_checkpoint(current_seed, total_scanned, args.mode)

            elapsed = time.time() - t_start

            if args.mode == "timestamp":
                try:
                    dt_str = datetime.fromtimestamp(current_seed - args.batch).strftime('%Y-%m-%d')
                except Exception:
                    dt_str = "Data?"
                print(f"  [📅 TIMESTAMP - GPU #{lote_num:04d}] Data: {dt_str} (TS: {current_seed - args.batch}) | Vel: {float(speed_str):.0f} MKeys/s | Total: {total_scanned:,} | Tempo: {elapsed:.1f}s", flush=True)
            else:
                print(f"  [🔢 40-BIT - GPU #{lote_num:04d}] Range: 0x{current_seed - args.batch:x} -> 0x{current_seed:x} | Vel: {float(speed_str):.0f} MKeys/s | Total: {total_scanned:,} | Tempo: {elapsed:.1f}s", flush=True)

            if "FOUND:1" in out_line:
                parts = dict(item.split(":") for item in out_line.split("|") if ":" in item)
                found_seed = int(parts.get("SEED", 0))
                print(f"\n🎉 HIT DETECTADO NA GPU CUDA! Verificando em C-Native CPU...", flush=True)
                if verify_full_seed(found_seed, known_db_loaded):
                    with open(WIN_FILE, "w", encoding="utf-8") as f:
                        f.write(f"PUZZLE #71 RESOLVIDO!\nSemente: {found_seed}\nData: {datetime.now().isoformat()}\n")
                    print("🏆 PUZZLE #71 RESOLVIDO COM SUCESSO!", flush=True)
                    return
    else:
        # MODO 2 & 4: STREAMING MULTI-THREAD CPU
        if args.mode == "sha256":
            gen = SeedGenerator.generate_sha256_timestamps(2015, 2015)
        elif args.mode == "40bit":
            gen = SeedGenerator.generate_40_48bit(start=start_seed_val if isinstance(start_seed_val, int) else 0)
        elif args.mode == "wordlist":
            gen = SeedGenerator.generate_wordlist_passphrases()
        else:
            gen = SeedGenerator.generate_timestamps(2015, 2015)

        batch = []
        cpu_batch = max(args.threads * 50, 1000)

        with multiprocessing.Pool(
            processes=args.threads,
            initializer=init_worker,
            initargs=(known_db_loaded,)
        ) as pool:
            try:
                for seed in gen:
                    batch.append(seed)
                    if len(batch) < cpu_batch: continue

                    lote_num += 1
                    salvar_checkpoint(batch[0], total_scanned, args.mode)

                    for res_seed in pool.imap_unordered(worker_check_seed_fast, batch, chunksize=100):
                        if res_seed is not None:
                            with open(WIN_FILE, "w", encoding="utf-8") as f:
                                f.write(f"PUZZLE #71 RESOLVIDO!\nSemente: {res_seed}\nData: {datetime.now().isoformat()}\n")
                            print("🏆 PUZZLE #71 RESOLVIDO COM SUCESSO!", flush=True)
                            return

                    total_scanned += len(batch)
                    last = batch[-1]
                    salvar_checkpoint(last, total_scanned, args.mode)

                    elapsed = time.time() - t_start
                    s_repr = last.hex()[:16] if isinstance(last, bytes) else str(last)
                    speed = total_scanned / elapsed if elapsed > 0 else 0

                    if args.mode == "sha256":
                        print(f"  [🔐 SHA256 - CPU #{lote_num:04d}] Úl. Hash: {s_repr} | Varridos: {total_scanned:,} ({speed:.1f} s/s) | Tempo: {elapsed:.1f}s", flush=True)
                    elif args.mode == "wordlist":
                        print(f"  [📝 WORDLIST - CPU #{lote_num:04d}] Úl. Pass: {s_repr} | Varridos: {total_scanned:,} ({speed:.1f} s/s) | Tempo: {elapsed:.1f}s", flush=True)
                    else:
                        print(f"  [⚙️ CPU #{lote_num:04d}] Semente: {s_repr} | Varridos: {total_scanned:,} ({speed:.1f} s/s) | Tempo: {elapsed:.1f}s", flush=True)

                    batch = []

            except KeyboardInterrupt:
                print(f"\n[!] Pausado pelo usuário. Total varrido: {total_scanned:,}", flush=True)

if __name__ == "__main__":
    main()
