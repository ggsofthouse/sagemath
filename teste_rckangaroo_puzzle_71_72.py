"""
TESTE RCKANGAROO E TESE SAGEMATH LLL GLV: PUZZLES #71 E #72
Autor: Antigravity AI Engine

Este script aplica o RCKangaroo e a tese de decomposição 2D GLV
para testar o processamento dos Puzzles #71 e #72.
"""

import os
import sys
import time
import hashlib
import binascii
import ecdsa
from fractions import Fraction
from typing import Tuple

SECP256k1 = ecdsa.SECP256k1
N = SECP256k1.order
G = SECP256k1.generator

LAMBDA_GLV = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72

PUZZLES = {
    71: {
        "bits": 71,
        "min_hex": 0x400000000000000000,
        "max_hex": 0x7FFFFFFFFFFFFFFFFF,
        "address": "1PWo3Jeb9jrGwfHDNpdGK54CRas7fsVzXU"
    },
    72: {
        "bits": 72,
        "min_hex": 0x800000000000000000,
        "max_hex": 0xFFFFFFFFFFFFFFFFFF,
        "address": "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR"
    }
}


def exact_lll(basis: list, delta: Fraction = Fraction(3, 4)) -> list:
    n = len(basis)
    m = len(basis[0])
    B = [list(row) for row in basis]

    def dot(u, v):
        return sum(u[i] * v[i] for i in range(len(u)))

    def compute_gram_schmidt(B_curr):
        ortho = [[Fraction(0) for _ in range(m)] for _ in range(n)]
        mu = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            ortho[i] = [Fraction(x) for x in B_curr[i]]
            for j in range(i):
                dot_ij = dot([Fraction(x) for x in B_curr[i]], ortho[j])
                dot_jj = dot(ortho[j], ortho[j])
                if dot_jj != 0:
                    mu[i][j] = dot_ij / dot_jj
                else:
                    mu[i][j] = Fraction(0)
                for col in range(m):
                    ortho[i][col] -= mu[i][j] * ortho[j][col]
        return ortho, mu

    ortho, mu = compute_gram_schmidt(B)
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Fraction(1, 2):
                val = mu[k][j]
                q = int(val + Fraction(1, 2)) if val >= 0 else int(val - Fraction(1, 2))
                if q != 0:
                    for col in range(m):
                        B[k][col] -= q * B[j][col]
                    ortho, mu = compute_gram_schmidt(B)

        norm_k = dot(ortho[k], ortho[k])
        norm_km1 = dot(ortho[k - 1], ortho[k - 1])

        if norm_k >= (delta - mu[k][k - 1] ** 2) * norm_km1:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            ortho, mu = compute_gram_schmidt(B)
            k = max(k - 1, 1)

    return B


def testar_tese_puzzles_71_72():
    print("=========================================================================")
    print("   TESTE DE TESE SAGEMATH LLL GLV + RCKANGAROO NOS PUZZLES #71 E #72")
    print("=========================================================================")

    for p_num, p_data in PUZZLES.items():
        print(f"\n--- EXECUTANDO TESTE NO PUZZLE #{p_num} ({p_data['bits']} BITS) ---")
        print(f"  Endereço: {p_data['address']}")
        print(f"  Range Hex: 0x{p_data['min_hex']:x} : 0x{p_data['max_hex']:x}")

        # Decomposição LLL GLV
        matrix = [[N, 0], [LAMBDA_GLV, 1]]
        t0 = time.time()
        B_red = exact_lll(matrix)
        t1 = time.time()

        u1, v1 = B_red[0][0], B_red[0][1]
        u2, v2 = B_red[1][0], B_red[1][1]

        b2 = round(p_data['min_hex'] * v1 / N)
        b1 = round(p_data['min_hex'] * v2 / N)

        k1 = p_data['min_hex'] - (b1 * u1 + b2 * u2)
        k2 = -(b1 * v1 + b2 * v2)

        print(f"  [+] Redução LLL GLV em {(t1 - t0)*1000:.2f} ms")
        print(f"  [+] Vetor Reduzido k1: {hex(int(k1))} ({int(k1).bit_length()} bits)")
        print(f"  [+] Vetor Reduzido k2: {hex(int(k2))} ({int(k2).bit_length()} bits)")
        
        # Gerar comando RCKangaroo correspondente
        print(f"\n  [+] Comando RCKangaroo Gerado para o Puzzle #{p_num}:")
        print(f"      python pool/worker/worker.py --puzzle {p_num} --name Local-GPU")

if __name__ == "__main__":
    testar_tese_puzzles_71_72()
