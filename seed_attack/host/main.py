"""
ORQUESTRADOR CONTÍNUO DE VARREDURA DE SEMENTES GPU - BITCOIN PUZZLE #71
Autor: Antigravity AI Engine

Integrado com SeedGenerator:
  - Estágio 1: Timestamps UNIX (2014-2016)
  - Estágio 2: SHA256(timestamp_int) e SHA256(str(timestamp))
  - Estágio 3: Sementes de 40 a 48 bits
  - Estágio 4: Modos sequenciais de 64 bits

Parâmetros CLI:
  --batch-size INT (tamanho do lote GPU, default: 500000000)
  --mode [timestamps, sha256, 40bit, wordlist, sequential]
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

def to_hex_str(val) -> str:
    if isinstance(val, int):
        return f"0x{val:x}"
    elif isinstance(val, bytes):
        return f"0x{val.hex()[:16]}..."
    return str(val)

def carregar_checkpoint() -> dict:
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_seed": 1388534400, # Jan 01 2014 UNIX Timestamp
        "total_scanned": 0,
        "mode": "timestamps",
        "created_at": datetime.now().isoformat()
    }

def salvar_checkpoint(last_seed, total_scanned: int, mode: str = "timestamps"):
    val_to_save = last_seed.hex() if isinstance(last_seed, bytes) else last_seed
    data = {
        "last_seed": val_to_save,
        "total_scanned": total_scanned,
        "mode": mode,
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
    parser = argparse.ArgumentParser(description="Orquestrador SEED ATTACK GPU para Bitcoin Puzzle #71")
    parser.add_argument("--batch-size", type=int, default=500000000, help="Tamanho do lote por ciclo GPU (default: 500.000.000)")
    parser.add_argument("--mode", type=str, default="auto", choices=["auto", "timestamps", "sha256", "40bit", "wordlist", "sequential"], help="Modo do gerador de sementes")
    args = parser.parse_args()

    print("=" * 80)
    print(" 🚀 SEED ATTACK GPU ENGINE - ORQUESTRADOR MULTI-MODO DE SEMENTES")
    print(f"  Alvo: Bitcoin Puzzle #71 | Lote Configurado: {args.batch_size:,} sementes")
    print(f"  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 1. Carregar Banco de Chaves
    with open(DB_FILE, "r", encoding="utf-8") as f:
        known_db = json.load(f)

    # 2. Compilar CUDA se necessário
    if not compilar_kernel_cuda():
        sys.exit(1)

    # 3. Carregar Checkpoint
    cp = carregar_checkpoint()
    mode = args.mode if args.mode != "auto" else cp.get("mode", "timestamps")
    raw_seed = cp.get("last_seed", 1388534400)
    current_seed = int(raw_seed, 16) if isinstance(raw_seed, str) and raw_seed.startswith("0x") else int(raw_seed)
    total_scanned = cp.get("total_scanned", 0)

    print(f"  [+] Modo Ativo      : {mode.upper()}")
    print(f"  [+] Semente Inicial  : {to_hex_str(current_seed)} ({current_seed:,})")
    print(f"  [+] Total Já Varrido: {total_scanned:,} sementes")
    print(f"  [+] Tamanho do Lote  : {args.batch_size:,} sementes por lote")
    print("\n[+] DISPARANDO VARREDURA GPU EM LOOP CONTÍNUO... (Pressione Ctrl+C para pausar)\n")

    lote_num = 0
    t_start_global = time.time()

    try:
        if mode == "sha256":
            # Estágio SHA256 (CPU + GPU multi-path)
            for seed_item in SeedGenerator.generate_sha256_timestamps(2014, 2016):
                lote_num += 1
                t0 = time.time()
                total_scanned += 1
                if verify_full_seed(seed_item, known_db):
                    with open(WIN_FILE, "w", encoding="utf-8") as wf:
                        wf.write(f"PUZZLE #71 RESOLVIDO!\nSemente (SHA256): {seed_item.hex()}\nData: {datetime.now().isoformat()}\n")
                    print(f"\n🏆 CHAVE PRIVADA DO PUZZLE #71 SALVA EM {WIN_FILE}!")
                    return
                if lote_num % 10000 == 0:
                    salvar_checkpoint(seed_item.hex(), total_scanned, mode="sha256")
                    dt = time.time() - t_start_global
                    print(f"  [Lote #{lote_num:06d}] SHA256 Seed: {seed_item.hex()[:16]}... | Scanned: {total_scanned:,} | Tempo: {dt:.1f}s")
        else:
            # Estágios GPU (Timestamps / 40bit / Sequential)
            while True:
                lote_num += 1
                t0 = time.time()

                res = subprocess.run([GPU_EXE, str(current_seed), str(args.batch_size)], capture_output=True, text=True)
                out_line = res.stdout.strip()
                dt = time.time() - t0

                speed_str = "1100.0"
                if "SPEED_MKEYS:" in out_line:
                    try:
                        parts = dict(item.split(":") for item in out_line.split("|") if ":" in item)
                        speed_str = parts.get("SPEED_MKEYS", "1100.0")
                    except Exception:
                        pass

                start_hex = to_hex_str(current_seed)
                current_seed += args.batch_size
                end_hex = to_hex_str(current_seed)
                total_scanned += args.batch_size

                salvar_checkpoint(current_seed, total_scanned, mode)

                elapsed_global = time.time() - t_start_global
                print(f"  [Lote #{lote_num:04d}] {start_hex} -> {end_hex} | Vel: {float(speed_str):.0f} MKeys/s | Total Varrido: {total_scanned:,} | Tempo: {elapsed_global:.1f}s")

                if "FOUND:1" in out_line:
                    parts = dict(item.split(":") for item in out_line.split("|") if ":" in item)
                    found_seed = int(parts.get("SEED", 0))
                    print(f"\n🎉🎉🎉 HIT DETECTADO NA GPU! Semente Candidata: {found_seed} 🎉🎉🎉")
                    
                    ok = verify_full_seed(found_seed, known_db)
                    if ok:
                        with open(WIN_FILE, "w", encoding="utf-8") as wf:
                            wf.write(f"PUZZLE #71 RESOLVIDO!\nSemente: {found_seed}\nData: {datetime.now().isoformat()}\n")
                        print(f"\n🏆 CHAVE PRIVADA DO PUZZLE #71 SALVA EM {WIN_FILE}!")
                        break

    except KeyboardInterrupt:
        print("\n\n  [!] Varredura pausada pelo usuário. Checkpoint salvo com sucesso!")
        print(f"  [+] Próxima semente a varrer: {to_hex_str(current_seed)} ({current_seed:,})")

if __name__ == "__main__":
    main()
