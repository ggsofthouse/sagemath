"""
EXCUTOR MESTRE DE ATAQUES - BITCOIN PUZZLE #71
Autor: Antigravity AI Engine

Permite executar qualquer um dos vetores de ataque otimizados com 1 único comando.
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def menu_principal():
    print("=" * 80)
    print(" 🚀 PAINEL MESTRE DE EXECUÇÃO DE ATAQUES - PUZZLE BITCOIN #71")
    print(f"  Diretório do Projeto: {BASE_DIR}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("\nEscolha a estratégia de ataque a ser executada:\n")
    print("  [1] ⚡ SEED ATTACK GPU (CUDA ~1.16 Bilhão sementes/seg - Timestamps 2014-2016)")
    print("  [2] 🔑 BIP32 HD-WALLET CPU (Unhardened 33-byte PubKey + Validação #65-#70)")
    print("  [3] 🧠 Z3 SMT SOLVER (Reconstrução Simbólica de PRNG de 64, 128 e 256 bits)")
    print("  [4] 🎲 ORQUESTRADOR DE ZONAS GPU (Intercalado 70% Z1 / 15% Z2 / 15% Z3 + Auto-Restart)")
    print("  [5] 🔐 SEED ATTACK SHA256 / 40-48 BITS (Hashes de Timestamps e Sementes Curtas)")
    print("  [0] Sair")
    print("\n" + "-" * 80)

def rodar_script(script_path: str, extra_args: list = None):
    cmd = [sys.executable, script_path]
    if extra_args:
        cmd.extend(extra_args)
    print(f"\n▶ Executando: {' '.join(cmd)}\n")
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[!] Processo pausado pelo usuário.")
    except Exception as e:
        print(f"\n[ERRO] Falha na execução: {e}")

def main():
    parser = argparse.ArgumentParser(description="Executor Mestre do Puzzle #71")
    parser.add_argument("--opcao", type=int, choices=[0, 1, 2, 3, 4, 5], help="Opção direta de ataque (1-5)")
    parser.add_argument("--batch-size", type=int, default=500000000, help="Tamanho do lote GPU")
    args = parser.parse_args()

    opcao = args.opcao

    if opcao is None:
        menu_principal()
        try:
            opcao_str = input("Digite o número da opção desejada [0-5]: ").strip()
            if not opcao_str.isdigit():
                print("Opção inválida.")
                return
            opcao = int(opcao_str)
        except KeyboardInterrupt:
            print("\nEncerrando.")
            return

    if opcao == 1:
        # Seed Attack GPU Timestamps
        rodar_script(os.path.join(BASE_DIR, "seed_attack", "host", "main.py"), ["--mode", "timestamps", "--batch-size", str(args.batch_size)])
    elif opcao == 2:
        # BIP32 HD-Wallet CPU
        rodar_script(os.path.join(BASE_DIR, "bip32_hdwallet_seed_search.py"))
    elif opcao == 3:
        # Z3 SMT Solver
        rodar_script(os.path.join(BASE_DIR, "bip32_z3_prng_solver.py"))
    elif opcao == 4:
        # Orquestrador de Zonas
        rodar_script(os.path.join(BASE_DIR, "puzzle71_randomized_runner.py"), ["--max-chunks", "100"])
    elif opcao == 5:
        # SHA256 / 40-bits
        rodar_script(os.path.join(BASE_DIR, "seed_attack", "host", "main.py"), ["--mode", "sha256"])
    elif opcao == 0:
        print("Saindo.")
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()
