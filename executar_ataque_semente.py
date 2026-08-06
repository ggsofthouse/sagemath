"""
EXECUTOR MESTRE DO ATAQUE DE SEMENTES & ENGENHARIA REVERSA BIP32 / PRNG - PUZZLE #71
Autor: Antigravity AI Engine

Arquitetura Otimizada:
  1. Detecção automática do total de threads CPU do sistema.
  2. Suporte a --resume e --from-mode para retenção e salto contínuo de progresso.
  3. Repasse unificado de parâmetros de batch-size, threads e modo.
  4. Execução de C-Native Engine via Coincurve.
"""

import os
import sys
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def menu_principal(threads: int):
    print("=" * 80)
    print(" 🚀 ORQUESTRADOR MESTRE DE ATAQUE DE SEMENTES & PRNG - BITCOIN PUZZLE #71")
    print(f"  Diretório: {BASE_DIR}")
    print(f"  Threads CPU Detectadas: {threads}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("\nEscolha a estratégia de Ataque de Semente:\n")
    print("  [1] ⚡ EXECUTAR VARREDURA COMPLETA DE SEMENTES EM SEQUÊNCIA AUTOMÁTICA")
    print("      (Timestamps 2013-2017 -> Hashes SHA256 -> 40-48bit -> Brainwallets -> Z3 Solver)")
    print("  [2] 📅 Modo Timestamps (UNIX Timestamps de 2013 a 2017)")
    print("  [3] 🔐 Modo SHA-256 (Hashes de Timestamps e Strings)")
    print("  [4] 🔢 Modo 40-48 bits (Sementes Inteiras de Baixa Entropia)")
    print("  [5] 📝 Modo Wordlist / Brainwallet (Palavras-chave + Passphrases 0-1000)")
    print("  [6] 🧠 Z3 SMT Solver (Reconstrução Simbólica de PRNG/LCG 64/128/256 bits)")
    print("  [7] ⚡ CUDA GPU Engine (Aceleração em Hardware HMAC-SHA512)")
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
    total_cores = multiprocessing.cpu_count()
    parser = argparse.ArgumentParser(description="Executor Mestre do Ataque de Sementes")
    parser.add_argument("--auto", action="store_true", help="Executa a sequência completa de ataques a sementes automaticamente")
    parser.add_argument("--opcao", type=int, choices=[0, 1, 2, 3, 4, 5, 6, 7], help="Opção direta de ataque")
    parser.add_argument("--batch-size", type=int, default=100000, help="Tamanho do lote por ciclo")
    parser.add_argument("--threads", type=int, default=total_cores, help=f"Número de threads CPU (default: {total_cores})")
    parser.add_argument("--from-mode", type=str, choices=["timestamp", "sha256", "40bit", "wordlist"], help="Iniciar a sequência a partir de um modo específico")
    args = parser.parse_args()

    opcao = 1 if args.auto else args.opcao

    if opcao is None:
        menu_principal(total_cores)
        try:
            opcao_str = input("Digite a opção desejada [0-7]: ").strip()
            if not opcao_str.isdigit():
                print("Opção inválida.")
                return
            opcao = int(opcao_str)
        except KeyboardInterrupt:
            print("\nEncerrando.")
            return

    main_script = os.path.join(BASE_DIR, "seed_attack", "host", "main.py")
    z3_script = os.path.join(BASE_DIR, "bip32_z3_prng_solver.py")

    modos = ["timestamp", "sha256", "40bit", "wordlist"]

    if opcao == 1:
        print(f"\n🚀 EXECUTANDO VARREDURA COMPLETA DE SEMENTES (THREADS: {args.threads})!\n")
        start_idx = 0
        if args.from_mode and args.from_mode in modos:
            start_idx = modos.index(args.from_mode)

        for mode in modos[start_idx:]:
            rodar_script(main_script, ["--mode", mode, "--threads", str(args.threads), "--batch-size", str(args.batch_size)])

        # Z3 Solver ao final
        rodar_script(z3_script)
    elif opcao == 2:
        rodar_script(main_script, ["--mode", "timestamp", "--threads", str(args.threads), "--batch-size", str(args.batch_size)])
    elif opcao == 3:
        rodar_script(main_script, ["--mode", "sha256", "--threads", str(args.threads), "--batch-size", str(args.batch_size)])
    elif opcao == 4:
        rodar_script(main_script, ["--mode", "40bit", "--threads", str(args.threads), "--batch-size", str(args.batch_size)])
    elif opcao == 5:
        rodar_script(main_script, ["--mode", "wordlist", "--threads", str(args.threads), "--batch-size", str(args.batch_size)])
    elif opcao == 6:
        rodar_script(z3_script)
    elif opcao == 7:
        rodar_script(main_script, ["--mode", "timestamp", "--use-gpu", "--batch-size", str(args.batch_size)])
    elif opcao == 0:
        print("Saindo.")
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()
