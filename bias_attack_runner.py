"""
ATAQUE DE BIAS ESTATÍSTICO - PUZZLE #71 (e outros)
Autor: Antigravity AI Engine

Estratégia: Com base nos offsets observados em 27+ puzzles resolvidos,
os puzzles #40-#69 mostraram concentração de 6-15% no range.
Este script executa o RCKangaroo priorizando as zonas de maior probabilidade
estatística PRIMEIRO, antes de varrer o resto do range.

Zonas de varredura (em ordem de prioridade):
  Zona 1 [ALTA PROB]:  0% - 15%   (onde #40-#69 foram encontrados)
  Zona 2 [MÉDIA PROB]: 15% - 30%  
  Zona 3 [MÉDIA PROB]: 50% - 65%  (onde #60 e #65 foram encontrados)
  Zona 4 [BAIXA PROB]: 30% - 50%  
  Zona 5 [BAIXA PROB]: 65% - 100%

Uso:
  python3 bias_attack_runner.py --puzzle 71 --gpus 0,1,2,3 --dp 14
  python3 bias_attack_runner.py --puzzle 71 --gpus 0,1,2,3 --dp 14 --zona 1
"""

import os
import sys
import time
import json
import argparse
import subprocess
from fractions import Fraction
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ============================================================
# ZONAS DE BIAS DERIVADAS DE ANÁLISE DOS PUZZLES RESOLVIDOS
# Baseado nos offsets reais dos puzzles #40 ao #69:
#   #40→8.74%, #45→9.28%, #50→8.16%, #55→8.80%
#   #60→23.53%, #65→53.46%, #66→7.85%, #67→11.09%, #68→9.80%, #69→6.28%
# ============================================================
BIAS_ZONES = [
    # (prioridade, nome, inicio%, fim%, razao)
    (1, "ALTA PROB [0-15%]",   0.00,  0.15,  "Concentracao maxima: #40,#45,#50,#55,#66,#68,#69"),
    (2, "ALTA PROB [15-25%]",  0.15,  0.25,  "Zona do Puzzle #60 (23.53%)"),
    (3, "MEDIA PROB [50-60%]", 0.50,  0.60,  "Zona do Puzzle #65 (53.46%)"),
    (4, "MEDIA PROB [25-40%]", 0.25,  0.40,  "Zona do Puzzle #25 (41.89%) e #130 (85%)"),
    (5, "MEDIA PROB [60-75%]", 0.60,  0.75,  "Zona do Puzzle #2 (50%), #3 (75%), #67 (11%)"),
    (6, "BAIXA PROB [40-50%]", 0.40,  0.50,  "Zona intermediaria"),
    (7, "BAIXA PROB [75-90%]", 0.75,  0.90,  "Zona do Puzzle #8 (84.38%), #15 (79.06%)"),
    (8, "BAIXA PROB [90-100%]",0.90,  1.00,  "Zona menos provavel estatisticamente"),
]

PUZZLES_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "puzzles_unsolved_database.json")


def carregar_puzzle_info(puzzle_num: int) -> dict:
    if os.path.exists(PUZZLES_DB_FILE):
        with open(PUZZLES_DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            for p in db.get("puzzles", []):
                if p["number"] == puzzle_num:
                    return p
    min_val = 1 << (puzzle_num - 1)
    max_val = (1 << puzzle_num) - 1
    return {
        "number": puzzle_num,
        "hex_min": f"{min_val:x}",
        "hex_max": f"{max_val:x}",
        "address": ""
    }


def compilar_se_necessario() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for sub in ["rckangaroo", "RCkangaroo"]:
        cands = [
            os.path.join(base_dir, sub, "build", "bin", "rckangaroo"),
            os.path.join(base_dir, sub, "build", "bin", "RCKangaroo"),
            os.path.join(base_dir, sub, "build", "RCKangaroo"),
        ]
        for c in cands:
            if os.path.exists(c):
                return os.path.abspath(c)
        folder = os.path.join(base_dir, sub)
        if os.path.exists(os.path.join(folder, "CMakeLists.txt")):
            print(f"[+] Compilando RCKangaroo em {folder}...")
            build_dir = os.path.join(folder, "build")
            os.makedirs(build_dir, exist_ok=True)
            subprocess.run(["cmake", ".."], cwd=build_dir, check=False)
            subprocess.run(["make", "-j4"], cwd=build_dir, check=False)
            for c in cands:
                if os.path.exists(c):
                    return os.path.abspath(c)
    return ""


def obter_telemetria_gpus() -> list:
    gpus_info = []
    try:
        res = subprocess.run([
            "nvidia-smi",
            "--query-gpu=index,name,temperature.gpu,power.draw,power.limit,utilization.gpu",
            "--format=csv,noheader,nounits"
        ], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            for line in res.stdout.strip().split("\n"):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 6:
                    gpus_info.append({
                        "index": parts[0], "name": parts[1],
                        "temp_c": parts[2], "power_w": parts[3],
                        "power_limit_w": parts[4], "util_pct": parts[5]
                    })
    except Exception:
        pass
    return gpus_info


def imprimir_mapa_bias(range_min: int, range_max: int, zona_ativa: int = None):
    """Exibe o mapa visual das zonas de bias no terminal."""
    span = range_max - range_min
    print("\n" + "=" * 75)
    print("   MAPA DE ZONAS DE BIAS ESTATÍSTICO (baseado em 27 puzzles resolvidos)")
    print("=" * 75)
    print(f"   Range Total: 0x{range_min:x} -> 0x{range_max:x}")
    print(f"   Span:        {span:,} chaves ({span.bit_length()} bits)\n")

    for pri, nome, p_ini, p_fim, razao in BIAS_ZONES:
        z_min = range_min + int(span * p_ini)
        z_max = range_min + int(span * p_fim)
        ativo = "  <<< PRÓXIMA " if zona_ativa == pri else ""
        bar_len = int((p_fim - p_ini) * 50)
        bar = "█" * bar_len
        estrelas = "⭐" * max(0, 4 - pri) + "  " * min(4, pri - 1)
        print(f"  P{pri} {estrelas} [{p_ini*100:4.0f}%-{p_fim*100:4.0f}%] {nome:<25} {ativo}")
        print(f"      {bar}")
        print(f"      0x{z_min:x} -> 0x{z_max:x}")
        print(f"      ({razao})\n")
    print("=" * 75)


def rodar_zona_bias(rckangaroo_bin: str, gpus_str: str, dp_bits: int,
                    zona_min: int, zona_max: int, zone_name: str,
                    address: str, pubkey: str) -> bool:
    """
    Executa RCKangaroo em uma zona específica do range.
    Usa o mesmo padrão do vastai_multi_gpu_runner.py que funciona:
      -gpu <mask>  -dp <N>  -range <bits>  -start <hex>
    O RCKangaroo gerencia todas as GPUs internamente em UM processo.
    Retorna True se chave privada encontrada.
    """
    # Máscara de GPUs: "0,1,2,3" -> "0123"
    gpu_mask = "".join(g.strip() for g in gpus_str.split(",") if g.strip())
    zone_span = zona_max - zona_min
    range_bits = zone_span.bit_length()

    print(f"\n{'='*75}")
    print(f"  DISPARANDO RCKangaroo na Zona: {zone_name}")
    print(f"  Start:      0x{zona_min:x}")
    print(f"  Range:      {range_bits} bits (~{zone_span:,} chaves)")
    print(f"  End (calc): 0x{zona_max:x}")
    print(f"  GPUs mask:  {gpu_mask}")
    print(f"{'='*75}\n")

    # Mesmo padrão exato do vastai_multi_gpu_runner.py que funcionava
    cmd = [
        rckangaroo_bin,
        "-gpu", gpu_mask,
        "-dp", str(dp_bits),
        "-range", str(range_bits),
        "-start", f"{zona_min:x}",
    ]
    if pubkey:
        cmd.extend(["-pubkey", pubkey])

    print(f"  [CMD] {' '.join(cmd)}\n")

    chave_encontrada = False
    start_time = time.time()
    last_telem_time = start_time

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        print(f"  [MONITOR] RCKangaroo PID={proc.pid} rodando...\n")

        for line in iter(proc.stdout.readline, ''):
            if not line:
                break
            line_s = line.rstrip()
            print(line_s, flush=True)

            # Detectar vitória
            if "PRIVATE KEY" in line_s.upper():
                print(f"\n{'*'*75}")
                print(f"**** CHAVE PRIVADA ENCONTRADA! PUZZLE RESOLVIDO! ****")
                print(f"**** {line_s} ****")
                print(f"{'*'*75}\n")
                chave_encontrada = True

            # Telemetria a cada 30s
            now = time.time()
            if now - last_telem_time >= 30:
                telem = obter_telemetria_gpus()
                if telem:
                    total_w = 0.0
                    parts = []
                    for g in telem:
                        try:
                            total_w += float(g['power_w'])
                        except Exception:
                            pass
                        parts.append(f"GPU{g['index']}:{g['temp_c']}C({g['power_w']}W)")
                    elapsed = now - start_time
                    print(f"\n  [TELEM {int(elapsed)}s] Total: {total_w:.0f}W | {' | '.join(parts)}\n")
                last_telem_time = now

        proc.wait()

    except KeyboardInterrupt:
        print("\n  [!] Interrompido pelo usuário.")
        try:
            proc.terminate()
        except Exception:
            pass
        raise

    elapsed = time.time() - start_time
    print(f"\n  [ZONA CONCLUÍDA] '{zone_name}' | Tempo: {elapsed:.1f}s | Chave: {'ENCONTRADA!' if chave_encontrada else 'nao encontrada'}")
    return chave_encontrada


def main():
    parser = argparse.ArgumentParser(
        description="Bias Attack Runner para Bitcoin Puzzles - Prioriza zonas estatísticas"
    )
    parser.add_argument("--puzzle", type=int, default=71, help="Número do puzzle alvo (default: 71)")
    parser.add_argument("--gpus", type=str, default="0,1,2,3", help="IDs das GPUs separados por vírgula")
    parser.add_argument("--dp", type=int, default=14, help="DP bits para RCKangaroo (min: 14)")
    parser.add_argument("--zona", type=int, default=0, help="Rodar apenas a zona N (0=todas em ordem)")
    parser.add_argument("--pubkey", type=str, default="", help="Chave pública alvo (se disponível)")
    args = parser.parse_args()

    print("\n" + "=" * 75)
    print("   BIAS ATTACK RUNNER - VARREDURA ESTATÍSTICA PRIORITÁRIA")
    print(f"   Puzzle #{args.puzzle} | GPUs: [{args.gpus}] | DP: {args.dp}")
    print(f"   Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75 + "\n")

    # Carregar info do puzzle
    p_info = carregar_puzzle_info(args.puzzle)
    range_min = int(p_info["hex_min"], 16)
    range_max = int(p_info["hex_max"], 16)
    address = p_info.get("address", "")
    pubkey = args.pubkey or p_info.get("pubkey", "")

    print(f"  [+] Endereço Alvo : {address}")
    print(f"  [+] PubKey        : {pubkey if pubkey else '(nao disponivel - Modo Benchmark)'}")
    print(f"  [+] Range         : 0x{range_min:x} -> 0x{range_max:x}")
    print(f"  [+] Span          : {(range_max - range_min):,} chaves")

    # Mapa de zonas
    imprimir_mapa_bias(range_min, range_max, zona_ativa=args.zona if args.zona > 0 else 1)

    # Localizar binário RCKangaroo
    rckangaroo_bin = compilar_se_necessario()
    if not rckangaroo_bin:
        print("\n[ERRO] RCKangaroo não encontrado! Compile primeiro:")
        print("  cd RCkangaroo && mkdir build && cd build && cmake .. && make -j4")
        sys.exit(1)
    print(f"\n  [+] RCKangaroo: {rckangaroo_bin}")

    # Telemetria inicial
    telem = obter_telemetria_gpus()
    if telem:
        print("\n  [+] Hardware Disponível:")
        total_w = 0.0
        for g in telem:
            try:
                total_w += float(g['power_w'])
            except Exception:
                pass
            print(f"      GPU {g['index']}: {g['name']} | {g['temp_c']}C | {g['util_pct']}% | {g['power_w']}W/{g['power_limit_w']}W")

    span = range_max - range_min

    # Selecionar zonas a executar
    if args.zona > 0:
        zonas = [z for z in BIAS_ZONES if z[0] == args.zona]
        if not zonas:
            print(f"\n[ERRO] Zona {args.zona} não existe! Use 1-{len(BIAS_ZONES)}")
            sys.exit(1)
    else:
        zonas = sorted(BIAS_ZONES, key=lambda z: z[0])

    # Rodar zona por zona em ordem de prioridade
    total_start = time.time()
    for prioridade, nome, p_ini, p_fim, razao in zonas:
        zona_min = range_min + int(span * p_ini)
        zona_max = range_min + int(span * p_fim)

        print(f"\n{'#'*75}")
        print(f"# INICIANDO ZONA PRIORIDADE {prioridade}: {nome}")
        print(f"# Razao: {razao}")
        print(f"{'#'*75}")

        try:
            encontrado = rodar_zona_bias(
                rckangaroo_bin=rckangaroo_bin,
                gpus_str=args.gpus,
                dp_bits=args.dp,
                zona_min=zona_min,
                zona_max=zona_max,
                zone_name=nome,
                address=address,
                pubkey=pubkey
            )
        except KeyboardInterrupt:
            print("\n[!] Sessão encerrada pelo usuário.")
            break

        if encontrado:
            print("\n" + "=" * 75)
            print("   *** PUZZLE RESOLVIDO! VERIFICAR O ARQUIVO RESULTS.TXT ***")
            print("=" * 75)
            break

    total_elapsed = time.time() - total_start
    print(f"\n[FIM] Tempo total de varredura bias: {total_elapsed/3600:.2f}h ({total_elapsed:.0f}s)")


if __name__ == "__main__":
    main()
