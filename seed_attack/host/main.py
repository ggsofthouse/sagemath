"""
ORQUESTRADOR MULTI-CORE 100% CPU - BITCOIN PUZZLE #71
Autor: Antigravity AI Engine

Utiliza MULTIPROCESSING para usar TODOS os núcleos do processador (100% CPU).
"""

import os
import sys
import json
import time
import argparse
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
DB_FILE  = os.path.join(BASE_DIR, "data", "known_keys.json")
CHECKPOINT_FILE = os.path.join(BASE_DIR, "data", "seed_checkpoint.json")
WIN_FILE = os.path.join(BASE_DIR, "SOLVED_PUZZLE71.txt")

def worker_check_seed(seed_item, known_db):
    """Função executada em paralelo em cada núcleo do CPU."""
    if verify_full_seed(seed_item, known_db):
        return seed_item
    return None

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

def main():
    num_cores = multiprocessing.cpu_count()
    parser = argparse.ArgumentParser(description="Orquestrador BIP32 Multi-Core 100% CPU")
    parser.add_argument("--batch", "--batch-size", type=int, default=1000, help="Tamanho do lote por ciclo")
    parser.add_argument("--workers", type=int, default=num_cores, help=f"Número de núcleos CPU (default: {num_cores})")
    parser.add_argument("--mode", type=str, default="timestamp",
                        choices=["timestamp", "sha256", "40bit", "wordlist"],
                        help="Tipo de semente a varrer via SeedGenerator")
    args = parser.parse_args()

    print("=" * 80, flush=True)
    print(f" 🚀 ORQUESTRADOR BIP32 MULTI-CORE (PARALELISMO EM {args.workers} NÚCLEOS CPU)", flush=True)
    print(f"  Modo Ativo: {args.mode.upper()} | Uso Total do Processador em Tempo Real", flush=True)
    print("=" * 80, flush=True)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        known_db = json.load(f)

    cp = carregar_checkpoint()
    total_scanned = cp.get("total_scanned", 0)
    start_seed_val = cp.get("last_seed", 1388534400)

    # Instanciar gerador
    if args.mode == "timestamp":
        gen = SeedGenerator.generate_timestamps(2014, 2016, count=10**12)
    elif args.mode == "sha256":
        gen = SeedGenerator.generate_sha256_timestamps(2014, 2016, count=10**12)
    elif args.mode == "40bit":
        gen = SeedGenerator.generate_40_48bit(start=start_seed_val if isinstance(start_seed_val, int) else 0, count=10**12)
    else:
        words = ["bitcoin", "satoshi", "puzzle", "nakamoto", "genesis", "secret"]
        gen = SeedGenerator.generate_wordlist_passphrases(words)

    lote_num = 0
    t_start = time.time()
    batch = []
    cpu_batch = max(args.workers * 10, args.batch)

    # Pool de multiprocessamento paralelo
    with multiprocessing.Pool(processes=args.workers) as pool:
        try:
            for seed in gen:
                batch.append(seed)

                if len(batch) < cpu_batch:
                    continue

                lote_num += 1

                # Checkpoint PRÉ-LOTE
                salvar_checkpoint(batch[0], total_scanned)

                # Processamento paralelo em TODOS OS NÚCLEOS DO CPU
                results = pool.starmap(worker_check_seed, [(s, known_db) for s in batch])

                for res_seed in results:
                    if res_seed is not None:
                        with open(WIN_FILE, "w", encoding="utf-8") as f:
                            f.write(f"PUZZLE #71 RESOLVIDO!\nSemente: {res_seed}\nData: {datetime.now().isoformat()}\n")
                        print("\n🏆 PUZZLE #71 RESOLVIDO COM SUCESSO!", flush=True)
                        return

                total_scanned += len(batch)
                last = batch[-1]

                # Checkpoint PÓS-LOTE
                salvar_checkpoint(last, total_scanned)

                elapsed = time.time() - t_start
                s_repr = last.hex()[:16] if isinstance(last, bytes) else str(last)
                speed = total_scanned / elapsed if elapsed > 0 else 0
                print(f"  [Lote #{lote_num:04d}] ÚLTIMA SEMENTE: {s_repr} | Varridos: {total_scanned:,} ({speed:.1f} sementes/s) | Tempo: {elapsed:.1f}s", flush=True)
                batch = []

        except KeyboardInterrupt:
            print(f"\n[!] Pausado pelo usuário. Total varrido: {total_scanned:,}", flush=True)

if __name__ == "__main__":
    main()
