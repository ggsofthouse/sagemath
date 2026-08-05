"""
PUZZLE #71 BIAS RANGE CALCULATOR & SUB-RANGE GENERATOR
Autor: Antigravity AI Engine

Calcula os sub-ranges otimizados de busca por densidade histórica de Puzzles (1 a 70).
Gera comandos hex prontos para KeyHunt / BitCrack (Address Mode).
"""

import sys
import math

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# =========================================================================
# BANCO DE DADOS COMPLETO: CHAVES PRIVADAS RESOLVIDAS (privatekeys.pw)
# =========================================================================
SOLVED_KEYS = {
    1:  0x1,
    2:  0x3,
    3:  0x7,
    4:  0x8,
    5:  0x15,
    6:  0x31,
    7:  0x4c,
    8:  0xe0,
    9:  0x1d3,
    10: 0x202,
    11: 0x483,
    12: 0xa7b,
    13: 0x1460,
    14: 0x2930,
    15: 0x68f3,
    16: 0xc936,
    17: 0x1764f,
    18: 0x3080d,
    19: 0x57a9f,
    20: 0xd2c55,
    25: 0x1fa5ee5,
    30: 0x3d94cd64,
    35: 0x4aed21170,
    40: 0xe9ae4933d6,
    45: 0x122fca143c05,
    50: 0x22bd43c2e9354,
    55: 0x6abe1f9b67e114,
    60: 0xfc07a1825367bbe,
    61: 0x13c96a3742f64906,
    62: 0x363d541eb611abee,
    63: 0x7cce5efdaccf6808,
    64: 0xf7051f27b09112d4,
    65: 0x1a838b13505b26867,
    66: 0x2832ed74f2b5e35ee,
    67: 0x730fc235c1942c1ae,
    68: 0xbebb3940cd0fc1491,
    69: 0x101d83275fb2bc7e0c,
    70: 0x349b84b6431a6c4ef1,
}

PUZZLE_TARGET = 71
TARGET_ADDRESS = "1PWo3Jeb9jrGwfHDNpdGK54CRas7fsVzXU"

MIN_PUZZLE_71 = 1 << (PUZZLE_TARGET - 1)  # 0x400000000000000000
MAX_PUZZLE_71 = (1 << PUZZLE_TARGET) - 1   # 0x7FFFFFFFFFFFFFFFFF
SPAN_PUZZLE_71 = MAX_PUZZLE_71 - MIN_PUZZLE_71 + 1

def calcular_estatisticas():
    ratios = []
    for n, key in sorted(SOLVED_KEYS.items()):
        min_n = 1 << (n - 1)
        max_n = (1 << n) - 1
        span_n = max_n - min_n + 1
        ratio = (key - min_n) / span_n
        ratios.append((n, ratio, key))

    ratios_sorted = sorted([r[1] for r in ratios])
    n_total = len(ratios_sorted)

    mean = sum(ratios_sorted) / n_total
    median = ratios_sorted[n_total // 2]
    q25 = ratios_sorted[int(n_total * 0.25)]
    q75 = ratios_sorted[int(n_total * 0.75)]

    return ratios, mean, median, q25, q75

def format_hex(val):
    return f"0x{val:018x}"

def main():
    print("=" * 80)
    print("  ANÁLISE ESTATÍSTICA DE BIAS & GERADOR DE SUB-RANGES - PUZZLE #71")
    print(f"  Endereço Alvo: {TARGET_ADDRESS}")
    print(f"  Range Total #71: {format_hex(MIN_PUZZLE_71)} -> {format_hex(MAX_PUZZLE_71)}")
    print(f"  Total de Chaves Resolvidas Analisadas: {len(SOLVED_KEYS)}")
    print("=" * 80)

    ratios, mean, median, q25, q75 = calcular_estatisticas()

    print("\nESTATÍSTICAS DA DISTRIBUIÇÃO HISTÓRICA DO CRIADOR:")
    print(f"  - Média relativa do range  : {mean*100:.2f}%")
    print(f"  - Mediana (P50)            : {median*100:.2f}%")
    print(f"  - Percentil 25 (P25)       : {q25*100:.2f}%")
    print(f"  - Percentil 75 (P75)       : {q75*100:.2f}%")
    print(f"  - Amplitude Interquartil   : [{q25*100:.2f}% a {q75*100:.2f}%]")

    print("\nHISTÓRICO RECENTE DE PUZZLES PRÓXIMOS (#60 a #70):")
    for n, r, k in ratios:
        if n >= 60:
            bar = "#" * int(r * 30)
            print(f"  Puzzle #{n:2d}: {r*100:6.2f}% | {bar:<30} | {hex(k)}")

    # Definição de Zonas Otimizadas por Densidade
    zonas = [
        ("ZONA 1: Mediana Central [40% - 65%]", 0.40, 0.65, "Contém a mediana (~55%) e os puzzles #68(49%), #70(64%), #65(66%)"),
        ("ZONA 2: Quartil Inferior [20% - 40%]", 0.20, 0.40, "Contém os puzzles #66(25.6%), #61(23.7%)"),
        ("ZONA 3: Quartil Superior [65% - 85%]", 0.65, 0.85, "Contém os puzzles #67(79.8%), #62(69.5%)"),
        ("ZONA 4: Topo Superior [85% - 100%]",   0.85, 1.00, "Contém os puzzles #60(96.9%), #63(95.0%), #64(93.0%)"),
        ("ZONA 5: Base Inferior [0% - 20%]",     0.00, 0.20, "Contém o puzzle #69(0.72%)"),
    ]

    print("\n" + "=" * 80)
    print("  SUB-RANGES OTIMIZADOS PARA O PUZZLE #71 (HEXADECIMAL)")
    print("=" * 80)

    for i, (nome, p_ini, p_fim, desc) in enumerate(zonas, 1):
        start_val = MIN_PUZZLE_71 + int(SPAN_PUZZLE_71 * p_ini)
        end_val = MIN_PUZZLE_71 + int(SPAN_PUZZLE_71 * p_fim) - 1
        sub_span = end_val - start_val + 1
        bits_sub = sub_span.bit_length()

        print(f"\n[{i}] {nome}")
        print(f"    Descrição : {desc}")
        print(f"    Hex Start : {format_hex(start_val)}")
        print(f"    Hex End   : {format_hex(end_val)}")
        print(f"    Tamanho   : {sub_span:,} chaves (~2^{bits_sub} bits)")

        print("    Comandos de Execução Prontos:")
        print(f"       * KeyHunt (Address Mode):")
        print(f"         keyhunt -m address -f {TARGET_ADDRESS} -r {format_hex(start_val)}:{format_hex(end_val)} -g")
        print(f"       * BitCrack (Address Mode):")
        print(f"         cuBitCrack -b 64 -t 256 -p 1024 -a {TARGET_ADDRESS} --range {format_hex(start_val)}:{format_hex(end_val)}")

    print("\n" + "=" * 80)
    print("DICA: Comece varrendo a ZONA 1 [40% - 65%]. Ela possui a maior concentração histórica.")
    print("=" * 80)

if __name__ == "__main__":
    main()
