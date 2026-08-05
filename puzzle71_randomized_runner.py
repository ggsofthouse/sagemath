"""
ORQUESTRADOR DE VARREDURA ALEATÓRIA COM CHECKPOINTING - BITCOIN PUZZLE #71
Autor: Antigravity AI Engine

Recursos:
  1. Divisão da zona em blocos (chunks) configuráveis (ex: 2^36 chaves por bloco).
  2. Seleção aleatória eficiente de blocos não-varridos (Randomized Jump Search).
  3. Gravador de progresso persistente (puzzle71_checkpoint.json) para evitar retrabalho.
  4. Suporte a execução via BitCrack (cuBitCrack) / KeyHunt ou modo de simulação.
"""

import os
import sys
import json
import time
import math
import random
import argparse
import subprocess
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CHECKPOINT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "puzzle71_checkpoint.json")
TARGET_ADDRESS  = "1PWo3Jeb9jrGwfHDNpdGK54CRas7fsVzXU"

ZONAS = {
    1: {"name": "ZONA 1 (Mediana 40-65%)", "start": 0x5999999999999a0000, "end": 0x69999999999999ffff},
    2: {"name": "ZONA 2 (Quartil Inf 20-40%)", "start": 0x4ccccccccccccd0000, "end": 0x59999999999999ffff},
    3: {"name": "ZONA 3 (Quartil Sup 65-85%)", "start": 0x6999999999999a0000, "end": 0x76666666666665ffff},
    4: {"name": "ZONA 4 (Topo Sup 85-100%)",   "start": 0x766666666666660000, "end": 0x7fffffffffffffffff},
    5: {"name": "ZONA 5 (Base Inf 0-20%)",     "start": 0x400000000000000000, "end": 0x4cccccccccccccffff},
}

def carregar_checkpoint() -> dict:
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Erro ao ler checkpoint: {e}. Criando novo.")
    return {
        "created_at": datetime.now().isoformat(),
        "target_address": TARGET_ADDRESS,
        "completed_chunks": [],
        "total_keys_scanned": 0
    }

def salvar_checkpoint(state: dict):
    state["updated_at"] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def encontrar_executavel():
    import shutil
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Locais locais comuns no projeto
    candidatos_locais = [
        os.path.join(base_dir, "cuBitCrack.exe"),
        os.path.join(base_dir, "cuBitCrack"),
        os.path.join(base_dir, "keyhunt.exe"),
        os.path.join(base_dir, "keyhunt"),
        os.path.join(base_dir, "tools", "cuBitCrack.exe"),
        os.path.join(base_dir, "tools", "keyhunt.exe"),
        os.path.join(base_dir, "BitCrack", "cuBitCrack.exe"),
        os.path.join(base_dir, "KeyHunt", "keyhunt.exe"),
    ]
    
    for cand in candidatos_locais:
        if os.path.exists(cand):
            t_type = "bitcrack" if "bitcrack" in os.path.basename(cand).lower() else "keyhunt"
            return os.path.abspath(cand), t_type
            
    # Procurar no PATH do sistema
    for exe in ["cuBitCrack", "cuBitCrack.exe", "keyhunt", "keyhunt.exe"]:
        path = shutil.which(exe)
        if path:
            return path, ("bitcrack" if "bitcrack" in exe.lower() else "keyhunt")
            
    return None, None

def main():
    parser = argparse.ArgumentParser(description="Orquestrador Aleatório com Checkpoint para Puzzle #71")
    parser.add_argument("--zona", type=int, default=1, choices=[1, 2, 3, 4, 5], help="Zona prioritária (1 a 5, default: 1)")
    parser.add_argument("--chunk-bits", type=int, default=36, help="Tamanho de cada bloco em bits (default: 36 -> ~68.7 bilhões de chaves)")
    parser.add_argument("--tool", type=str, default="auto", choices=["auto", "bitcrack", "keyhunt", "dry-run"], help="Ferramenta a usar")
    parser.add_argument("--max-chunks", type=int, default=3, help="Máximo de blocos a processar nesta rodada (default: 3)")
    args = parser.parse_args()

    zona_info = ZONAS[args.zona]
    z_start = zona_info["start"]
    z_end   = zona_info["end"]
    chunk_size = 1 << args.chunk_bits

    total_keys_zone = z_end - z_start + 1
    num_chunks = math.ceil(total_keys_zone / chunk_size)

    state = carregar_checkpoint()
    completed_set = set(state.get("completed_chunks", []))

    print("=" * 80)
    print(" 🎲 ORQUESTRADOR ALEATÓRIO COM PERSISTÊNCIA - PUZZLE #71")
    print(f"  Alvo:            {TARGET_ADDRESS}")
    print(f"  Zona Selecionada: {zona_info['name']}")
    print(f"  Range da Zona:   0x{z_start:018x} -> 0x{z_end:018x}")
    print(f"  Tamanho Bloco:   2^{args.chunk_bits} ({chunk_size:,} chaves)")
    print(f"  Total de Blocos: {num_chunks:,}")
    print(f"  Blocos Concluídos: {len(completed_set):,} / {num_chunks:,} ({len(completed_set)/num_chunks*100:.4f}%)")
    print(f"  Arquivo Checkpoint: {CHECKPOINT_FILE}")
    print("=" * 80)

    exe_path = None
    tool_type = args.tool
    if tool_type == "auto":
        exe_path, tool_type = encontrar_executavel()
        if not exe_path:
            print("\n[!] Nenhuma ferramenta GPU (cuBitCrack/keyhunt) encontrada no PATH ou na pasta do projeto.")
            print("[!] Entrando em MODO DRY-RUN (Simulação de Orquestração).")
            tool_type = "dry-run"

    print(f"\n[+] Modo de Execução: {tool_type.upper()} ({exe_path or 'Simulado'})")

    if len(completed_set) >= num_chunks:
        print("\n🎉 Todos os blocos desta zona já foram varridos no checkpoint!")
        return

    processed_count = 0

    while processed_count < args.max_chunks and len(completed_set) < num_chunks:
        chunk_id = random.randint(0, num_chunks - 1)
        if chunk_id in completed_set:
            continue

        processed_count += 1
        c_start = z_start + (chunk_id * chunk_size)
        c_end   = min(c_start + chunk_size - 1, z_end)

        c_start_hex = f"0x{c_start:018x}"
        c_end_hex   = f"0x{c_end:018x}"

        print("-" * 80)
        print(f"▶ Processando Bloco [{processed_count}/{args.max_chunks}] (ID do Bloco #{chunk_id:,})")
        print(f"  Sub-Range: {c_start_hex} -> {c_end_hex}")

        cmd = []
        if tool_type == "bitcrack":
            cmd = [exe_path, "-b", "64", "-t", "256", "-p", "1024", "-a", TARGET_ADDRESS, "--range", f"{c_start_hex}:{c_end_hex}"]
        elif tool_type == "keyhunt":
            cmd = [exe_path, "-m", "address", "-f", TARGET_ADDRESS, "-r", f"{c_start_hex}:{c_end_hex}", "-g"]
        else: # dry-run
            cmd = [f"cuBitCrack -a {TARGET_ADDRESS} --range {c_start_hex}:{c_end_hex}"]

        print(f"  Comando: {' '.join(cmd)}")

        t0 = time.time()
        encontrado = False

        if tool_type != "dry-run":
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    line_str = line.strip()
                    print(line_str)
                    if "PRIVATE KEY" in line_str.upper() or "FOUND" in line_str.upper():
                        encontrado = True
                        print(f"\n🎉 CHAVE PRIVADA ENCONTRADA: {line_str}\n")
                        break
                proc.wait()
            except Exception as e:
                print(f"[ERRO ao executar bloco]: {e}")
        else:
            time.sleep(0.2)

        dt = time.time() - t0

        completed_set.add(chunk_id)
        state["completed_chunks"] = list(completed_set)
        state["total_keys_scanned"] = state.get("total_keys_scanned", 0) + (c_end - c_start + 1)
        salvar_checkpoint(state)

        print(f"  [OK] Bloco #{chunk_id:,} concluído em {dt:.2f}s. Progresso gravado no checkpoint.")

        if encontrado:
            print("\n🏆 PUZZLE #71 RESOLVIDO COM SUCESSO!")
            break

if __name__ == "__main__":
    main()
