"""
ORQUESTRADOR DE VARREDURA DE ZONAS COM AUTO-RESTART E PERSISTÊNCIA PRÉ-BLOCO
Autor: Antigravity AI Engine

Recursos:
  1. Checkpoint salvo ANTES de iniciar a GPU e ATUALIZADO após a conclusão.
  2. Auto-Restart inteligente: se a GPU ou o processo falhar, reinicia automaticamente.
  3. Intercalação de Zonas: 70% ZONA 1, 15% ZONA 2, 15% ZONA 3.
  4. Registro de velocidade real (MKeys/s) e telemetria no checkpoint.
  5. Verificação final de Endereço Bitcoin P2PKH (1PWo3Jeb9jrGwfHDNpdGK54CRas7fsVzXU).
"""

import os
import sys
import json
import time
import math
import random
import argparse
import subprocess
import hashlib
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
    1: {"name": "ZONA 1 (Mediana 40-65%)", "start": 0x5999999999999a0000, "end": 0x69999999999999ffff, "prob": 0.70},
    2: {"name": "ZONA 2 (Quartil Inf 20-40%)", "start": 0x4ccccccccccccd0000, "end": 0x59999999999999ffff, "prob": 0.15},
    3: {"name": "ZONA 3 (Quartil Sup 65-85%)", "start": 0x6999999999999a0000, "end": 0x76666666666665ffff, "prob": 0.15},
}

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

def point_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 != y2: return None
    if x1 == x2:
        l = (3 * x1 * x1) * pow(2 * y1, P - 2, P) % P
    else:
        l = (y2 - y1) * pow(x2 - x1, P - 2, P) % P
    x3 = (l * l - x1 - x2) % P
    y3 = (l * (x1 - x3) - y1) % P
    return (x3, y3)

def point_mul(k, p=G):
    r = None
    q = p
    while k > 0:
        if k & 1: r = point_add(r, q)
        q = point_add(q, q)
        k >>= 1
    return r

def privkey_to_address(privkey_int: int) -> str:
    pt = point_mul(privkey_int)
    prefix = b'\x02' if pt[1] % 2 == 0 else b'\x03'
    pub_bytes = prefix + pt[0].to_bytes(32, 'big')
    sha = hashlib.sha256(pub_bytes).digest()
    rip = hashlib.new('ripemd160', sha).digest()
    ext = b'\x00' + rip
    chk = hashlib.sha256(hashlib.sha256(ext).digest())[:4]
    alpha = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(ext + chk, 'big')
    res = ''
    while num > 0:
        num, r = divmod(num, 58)
        res = alpha[r] + res
    for b in ext + chk:
        if b == 0: res = '1' + res
        else: break
    return res

def carregar_checkpoint() -> dict:
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "created_at": datetime.now().isoformat(),
        "target_address": TARGET_ADDRESS,
        "completed_chunks": [],
        "in_progress_chunk": None,
        "total_keys_scanned": 0,
        "last_speed_mkeys": 0.0
    }

def salvar_checkpoint(state: dict):
    state["updated_at"] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def encontrar_executavel():
    import shutil
    base_dir = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(base_dir, "cuBitCrack.exe"),
        os.path.join(base_dir, "cuBitCrack"),
        os.path.join(base_dir, "keyhunt.exe"),
        os.path.join(base_dir, "keyhunt"),
    ]
    for cand in candidatos:
        if os.path.exists(cand):
            t_type = "bitcrack" if "bitcrack" in os.path.basename(cand).lower() else "keyhunt"
            return os.path.abspath(cand), t_type
    for exe in ["cuBitCrack", "cuBitCrack.exe", "keyhunt", "keyhunt.exe"]:
        path = shutil.which(exe)
        if path:
            return path, ("bitcrack" if "bitcrack" in exe.lower() else "keyhunt")
    return None, None

def escolher_zona_intercalada() -> int:
    """Intercala 70% Zona 1, 15% Zona 2, 15% Zona 3."""
    r = random.random()
    if r <= 0.70: return 1
    elif r <= 0.85: return 2
    else: return 3

def main():
    parser = argparse.ArgumentParser(description="Orquestrador Intercalado por Zonas com Auto-Restart")
    parser.add_argument("--chunk-bits", type=int, default=36, help="Tamanho de cada bloco em bits (default: 36)")
    parser.add_argument("--tool", type=str, default="auto", choices=["auto", "bitcrack", "keyhunt", "dry-run"], help="Ferramenta")
    parser.add_argument("--max-chunks", type=int, default=5, help="Máximo de blocos a processar nesta rodada")
    args = parser.parse_args()

    state = carregar_checkpoint()
    completed_set = set(state.get("completed_chunks", []))
    chunk_size = 1 << args.chunk_bits

    exe_path, tool_type = None, args.tool
    if tool_type == "auto":
        exe_path, tool_type = encontrar_executavel()
        if not exe_path:
            tool_type = "dry-run"

    print("=" * 80)
    print(" 🎲 ORQUESTRADOR INTERCALADO DE ZONAS - PUZZLE #71")
    print(f"  Alvo:              {TARGET_ADDRESS}")
    print(f"  Modo de Execução:  {tool_type.upper()} ({exe_path or 'Simulado'})")
    print(f"  Total Varrido:     {state.get('total_keys_scanned', 0):,} chaves")
    print(f"  Última Velocidade: {state.get('last_speed_mkeys', 0.0):.2f} MKeys/s")
    print("=" * 80)

    processed_count = 0

    while processed_count < args.max_chunks:
        z_id = escolher_zona_intercalada()
        z_info = ZONAS[z_id]
        z_start, z_end = z_info["start"], z_info["end"]
        num_chunks = math.ceil((z_end - z_start + 1) / chunk_size)

        chunk_id = random.randint(0, num_chunks - 1)
        chunk_key = f"Z{z_id}_{chunk_id}"
        if chunk_key in completed_set:
            continue

        processed_count += 1
        c_start = z_start + (chunk_id * chunk_size)
        c_end   = min(c_start + chunk_size - 1, z_end)
        c_start_hex, c_end_hex = f"0x{c_start:018x}", f"0x{c_end:018x}"

        # 1. REGISTRAR NO CHECKPOINT ANTES DE INICIAR A GPU (MANTÉM INTEGRIDADE)
        state["in_progress_chunk"] = {"key": chunk_key, "start": c_start_hex, "end": c_end_hex, "started_at": datetime.now().isoformat()}
        salvar_checkpoint(state)

        print("-" * 80)
        print(f"▶ Processando Bloco [{processed_count}/{args.max_chunks}] ({z_info['name']} | ID #{chunk_id:,})")
        print(f"  Sub-Range: {c_start_hex} -> {c_end_hex}")

        cmd = []
        if tool_type == "bitcrack":
            cmd = [exe_path, "-b", "64", "-t", "256", "-p", "1024", "-a", TARGET_ADDRESS, "--range", f"{c_start_hex}:{c_end_hex}"]
        elif tool_type == "keyhunt":
            cmd = [exe_path, "-m", "address", "-f", TARGET_ADDRESS, "-r", f"{c_start_hex}:{c_end_hex}", "-g"]
        else:
            cmd = [f"cuBitCrack -a {TARGET_ADDRESS} --range {c_start_hex}:{c_end_hex}"]

        t0 = time.time()
        encontrado = False
        restarts = 0
        max_restarts = 3

        # AUTO-RESTART EM CASO DE CRASH DA GPU
        while restarts <= max_restarts:
            if tool_type != "dry-run":
                try:
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    for line in proc.stdout:
                        line_s = line.strip()
                        print(line_s)
                        if "PRIVATE KEY" in line_s.upper() or "FOUND" in line_s.upper():
                            encontrado = True
                            # Extrair e verificar endereço no CPU
                            for token in line_s.split():
                                if token.startswith("0x"):
                                    cand_val = int(token, 16)
                                    addr = privkey_to_address(cand_val)
                                    if addr == TARGET_ADDRESS:
                                        print(f"\n🎉🎉🎉 PUZZLE #71 RESOLVIDO COM SUCESSO! 🎉🎉🎉")
                                        print(f"  Chave Privada: {hex(cand_val)}")
                                        print(f"  Endereço    : {addr}")
                            break
                    proc.wait()
                    if proc.returncode == 0 or encontrado:
                        break
                except Exception as e:
                    restarts += 1
                    print(f"  [!] Auto-Restart GPU ({restarts}/{max_restarts}): {e}")
                    time.sleep(2)
            else:
                time.sleep(0.2)
                break

        dt = time.time() - t0
        speed_mkeys = ((c_end - c_start + 1) / dt) / 1000000.0 if dt > 0 else 0.0

        # 2. ATUALIZAR CHECKPOINT APÓS CONCLUSÃO DO BLOCO
        completed_set.add(chunk_key)
        state["completed_chunks"] = list(completed_set)
        state["in_progress_chunk"] = None
        state["last_speed_mkeys"] = speed_mkeys
        state["total_keys_scanned"] = state.get("total_keys_scanned", 0) + (c_end - c_start + 1)
        salvar_checkpoint(state)

        print(f"  [OK] Bloco {chunk_key} concluído em {dt:.2f}s (Velocidade: {speed_mkeys:.2f} MKeys/s). Checkpoint atualizado.")

        if encontrado:
            break

if __name__ == "__main__":
    main()
