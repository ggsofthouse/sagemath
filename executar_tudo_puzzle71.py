"""
EXECUTOR MESTRE AUTOMATIZADO - BITCOIN PUZZLE #71
Autor: Antigravity AI Engine

Executa os vetores de ataque em sequência automática ou permite selecionar um modo individual.
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
    print("\nEscolha a forma de execução:\n")
    print("  [1] ⚡ EXECUTAR TODOS EM SEQUÊNCIA AUTOMÁTICA (Timestamps -> SHA256 -> 40-bits -> Z3 Solver)")
    print("  [2] 🔑 Modo Timestamps (2014-2016)")
    print("  [3] 🔐 Modo SHA256 (Hashes de Timestamps)")
    print("  [4] 🔢 Modo 40-Bits (Sementes Inteiras de 40 a 48 bits)")
    print("  [5] 🧠 Z3 SMT Solver (Reconstrução Simbólica 64/128/256 bits)")
    print("  [6] 🎲 Orquestrador de Zonas GPU (Intercalado 70% Z1 / 15% Z2 / 15% Z3)")
    print("  [0] Sair")
    print("\n" + "-" * 80)

def rodar_script(script_path: str, extra_args: list = None):
    cmd = [sys.executable, script_path]
    if extra_args:
        cmd.extend(extra_args)
    print(f"\n▶ [INICIANDO] {' '.join(cmd)}\n", flush=True)
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n[!] Etapa pausada pelo usuário.", flush=True)
    except Exception as e:
        print(f"\n[ERRO] Falha na execução da etapa: {e}", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Executor Mestre Automatizado do Puzzle #71")
    parser.add_argument("--auto", action="store_true", help="Executa a sequência completa de ataques em linha automaticamente")
    parser.add_argument("--opcao", type=int, choices=[0, 1, 2, 3, 4, 5, 6], help="Opção direta de ataque")
    args = parser.parse_args()

    if args.auto:
        opcao = 1
    else:
        opcao = args.opcao

    if opcao is None:
        menu_principal()
        try:
            opcao_str = input("Digite a opção desejada [0-6]: ").strip()
            if not opcao_str.isdigit():
                print("Opção inválida.")
                return
            opcao = int(opcao_str)
        except KeyboardInterrupt:
            print("\nEncerrando.")
            return

    main_script = os.path.join(BASE_DIR, "seed_attack", "host", "main.py")
    z3_script = os.path.join(BASE_DIR, "bip32_z3_prng_solver.py")
    zones_script = os.path.join(BASE_DIR, "puzzle71_randomized_runner.py")

    if opcao == 1:
        print("\n🚀 INICIANDO SEQUÊNCIA AUTOMÁTICA EM LINHA DE TODOS OS ATAQUES!\n")
        # 1. Timestamps
        rodar_script(main_script, ["--mode", "timestamp"])
        # 2. Hashes SHA256
        rodar_script(main_script, ["--mode", "sha256"])
        # 3. 40-bits
        rodar_script(main_script, ["--mode", "40bit"])
        # 4. Z3 SMT Solver
        rodar_script(z3_script)
    elif opcao == 2:
        rodar_script(main_script, ["--mode", "timestamp"])
    elif opcao == 3:
        rodar_script(main_script, ["--mode", "sha256"])
    elif opcao == 4:
        rodar_script(main_script, ["--mode", "40bit"])
    elif opcao == 5:
        rodar_script(z3_script)
    elif opcao == 6:
        rodar_script(zones_script, ["--max-chunks", "100"])
    elif opcao == 0:
        print("Saindo.")
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()
