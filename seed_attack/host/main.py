"""
ORQUESTRADOR CONTÍNUO DE VARREDURA DE SEMENTES BIP32 (CPU MULTI-PATH CRIPTOGRÁFICO)
Autor: Antigravity AI Engine

Executa varredura 100% fiel à especificação oficial BIP32:
  - HMAC-SHA512 com "Bitcoin seed"
  - Derivação Unhardened com Chave Pública Comprimida de 33 bytes (secp256k1)
  - Validação estrita em 4 caminhos simultâneos (m/0/n, m/n, m/0'/n, m/44'/0'/0'/0/n)
  - Máscara 2^(n-1) + (raw mod 2^(n-1)) contra Puzzles #65 a #70
"""

import os
import sys
import json
import time
import argparse
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
    parser = argparse.ArgumentParser(description="Orquestrador BIP32 Multi-Path 100% Criptográfico")
    parser.add_argument("--batch", "--batch-size", type=int, default=1000, help="Tamanho do lote por ciclo de checagem")
    parser.add_argument("--mode", type=str, default="timestamp",
                        choices=["timestamp", "sha256", "40bit", "wordlist"],
                        help="Tipo de semente a varrer via SeedGenerator")
    args = parser.parse_args()

    print("=" * 80)
    print(" 🚀 ORQUESTRADOR BIP32 MULTI-PATH 100% CRIPTOGRÁFICO - BITCOIN PUZZLE #71")
    print(f"  Modo Ativo: {args.mode.upper()} | Validação Criptográfica Real em 4 Caminhos BIP32")
    print("=" * 80)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        known_db = json.load(f)

    cp = carregar_checkpoint()
    total_scanned = cp.get("total_scanned", 0)
    start_seed_val = cp.get("last_seed", 1388534400)

    # Instanciar o SeedGenerator
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
    cpu_batch = min(args.batch, 2000) # Lote ideal para resposta contínua

    try:
        for seed in gen:
            batch.append(seed)

            if len(batch) < cpu_batch:
                continue

            lote_num += 1

            # Checkpoint PRÉ-LOTE para resiliência
            salvar_checkpoint(batch[0], total_scanned)

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
            print(f"  [Lote #{lote_num:04d}] ÚLTIMA SEMENTE: {s_repr} | Varridos: {total_scanned:,} | Tempo: {elapsed:.1f}s")
            batch = []

    except KeyboardInterrupt:
        print(f"\n[!] Pausado pelo usuário. Total varrido: {total_scanned:,}")

if __name__ == "__main__":
    main()
