"""
TESTE 1: LLL HNP Solver em Ranges Específicos de Puzzles Bitcoin
Autor: Antigravity AI Engine

Este script testa a recuperação de chaves privadas em ranges reais de Puzzles Bitcoin
(ex: Puzzle 40, Puzzle 60, Puzzle 65) usando Redução de Redes (LLL).
"""

import random
import time
from fractions import Fraction
from typing import List, Tuple

# Ordem da Curva Elíptica secp256k1 (N)
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def exact_lll(basis: List[List[int]], delta: Fraction = Fraction(3, 4)) -> List[List[int]]:
    """
    Algoritmo LLL de Aritmética Racional Exata (fractions.Fraction).
    Reduz a base da rede sem erros de arredondamento de ponto flutuante.
    """
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


def executar_teste_puzzle(puzzle_num: int, leak_bits: int = 64, num_signatures: int = 5):
    """
    Executa o Teste 1 para um Puzzle Bitcoin específico (ex: Puzzle 40, 60, 65).
    """
    min_range = 1 << (puzzle_num - 1)
    max_range = (1 << puzzle_num) - 1

    print("=========================================================================")
    print(f"   TESTE 1: RECOVERY LLL NO PUZZLE #{puzzle_num}")
    print(f"   Range do Puzzle: [{hex(min_range)} ... {hex(max_range)}]")
    print(f"   Vazamento de Nonce: {leak_bits} bits | Assinaturas Utilizadas: {num_signatures}")
    print("=========================================================================")

    # 1. Gerar Chave Privada Real dentro do Range Exato do Puzzle
    chave_privada_puzzle = random.randint(min_range, max_range)
    print(f"[+] Chave Privada Gerada no Range: {hex(chave_privada_puzzle)}")

    X = N >> leak_bits
    m = num_signatures

    # 2. Simular Assinaturas ECDSA com Nonce Vazado (k < X)
    t_list = []
    u_list = []
    signatures = []

    for _ in range(m):
        k = random.randint(1, X)
        z = random.randint(1, N - 1)
        r = random.randint(1, N - 1)
        s = (pow(k, -1, N) * (z + r * chave_privada_puzzle)) % N

        s_inv = pow(s, -1, N)
        t = (s_inv * r) % N
        u = (s_inv * z) % N
        t_list.append(t)
        u_list.append(u)
        signatures.append((k, r, s, z))

    # 3. Construir Matriz de Kannan Escala
    scale = 1 << leak_bits
    rows = []
    for i in range(m):
        r = [0] * (m + 2)
        r[i] = N * scale
        rows.append(r)

    rows.append([t * scale for t in t_list] + [1, 0])
    rows.append([u * scale for u in u_list] + [0, X * scale])

    # 4. Executar Redução LLL
    t0 = time.time()
    B_red = exact_lll(rows)
    t1 = time.time()

    tempo_ms = (t1 - t0) * 1000
    print(f"[+] Redução de Matriz LLL concluída em {tempo_ms:.2f} milissegundos")

    # 5. Extração da Chave Privada
    recuperada = False
    for i in range(len(B_red)):
        cand_d1 = int(B_red[i][m]) % N
        cand_d2 = int(-B_red[i][m]) % N

        for cand in [cand_d1, cand_d2]:
            if cand == chave_privada_puzzle:
                print(f"\n[SUCESSO COMPROVADO] Chave Privada Extraída na Linha {i}:")
                print(f"                      {hex(cand)}")
                print(f"                      Pertence ao Puzzle #{puzzle_num}? SIM!")
                recuperada = True
                break
        if recuperada:
            break

    if not recuperada:
        print("\n[FALHA] Chave não encontrada na base reduzida.")

    return recuperada


if __name__ == "__main__":
    # Teste A: Puzzle 40 (Range 2^39 .. 2^40 - 1)
    executar_teste_puzzle(puzzle_num=40, leak_bits=64, num_signatures=5)
    print("\n")
    # Teste B: Puzzle 60 (Range 2^59 .. 2^60 - 1)
    executar_teste_puzzle(puzzle_num=60, leak_bits=64, num_signatures=5)
    print("\n")
    # Teste C: Puzzle 65 (Range 2^64 .. 2^65 - 1)
    executar_teste_puzzle(puzzle_num=65, leak_bits=64, num_signatures=5)
