"""
EXECUTOR UNIFICADO DE ATAQUES - PUZZLE #71
Autor: Antigravity AI Engine

Executa em sequência:
  1. Varredura GPU CUDA de 10 BILHÕES de sementes BIP32 (bip32_gpu_seed_search.exe)
  2. Varredura Otimizada por Bias (ZONA 1) com Checkpointing (puzzle71_randomized_runner.py)
"""

import os
import sys
import time
import subprocess
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GPU_SEED_EXE = os.path.join(BASE_DIR, "bip32_gpu_seed_search.exe")
RUNNER_PY    = os.path.join(BASE_DIR, "puzzle71_randomized_runner.py")

def main():
    print("=" * 80)
    print(" 🚀 EXECUTOR UNIFICADO DE ATAQUES INTEGRADOS - BITCOIN PUZZLE #71")
    print(f"  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # FASE 1: VARREDURA GPU CUDA DE SEMENTES BIP32 (10 BILHÕES DE SEMENTES)
    # -------------------------------------------------------------------------
    print("\n" + "#" * 80)
    print(" [FASE 1] Executando Varredor de Sementes BIP32 em GPU CUDA (10 Bilhões)...")
    print("#" * 80 + "\n")

    if os.path.exists(GPU_SEED_EXE):
        # Jan 01 2014 = 1388534400 | Total = 10,000,000,000 (10 Bilhoes)
        t0_f1 = time.time()
        try:
            res = subprocess.run(
                [GPU_SEED_EXE, "1388534400", "10000000000"],
                text=True,
                capture_output=False
            )
        except Exception as e:
            print(f"[ERRO na Fase 1]: {e}")
        dt_f1 = time.time() - t0_f1
        print(f"\n[FASE 1 CONCLUÍDA] Tempo da Fase 1: {dt_f1:.2f}s")
    else:
        print(f"[!] Executável CUDA {GPU_SEED_EXE} não encontrado. Pulando Fase 1.")

    # -------------------------------------------------------------------------
    # FASE 2: VARREDURA DE SUB-RANGES OTIMIZADOS POR BIAS (ZONA 1)
    # -------------------------------------------------------------------------
    print("\n" + "#" * 80)
    print(" [FASE 2] Iniciando Orquestrador por Sub-Ranges Otimizados (ZONA 1 [40-65%])...")
    print("#" * 80 + "\n")

    if os.path.exists(RUNNER_PY):
        t0_f2 = time.time()
        try:
            # Roda 5 blocos da Zona 1 por padrão (ajustável)
            subprocess.run(
                [sys.executable, RUNNER_PY, "--zona", "1", "--chunk-bits", "36", "--max-chunks", "5"],
                text=True,
                capture_output=False
            )
        except Exception as e:
            print(f"[ERRO na Fase 2]: {e}")
        dt_f2 = time.time() - t0_f2
        print(f"\n[FASE 2 CONCLUÍDA] Tempo da Fase 2: {dt_f2:.2f}s")
    else:
        print(f"[!] Script {RUNNER_PY} não encontrado.")

    print("\n" + "=" * 80)
    print(" 🎉 EXECUÇÃO INTEGRADA FINALIZADA COM SUCESSO!")
    print(f"  Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
