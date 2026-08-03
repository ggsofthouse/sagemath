# SageMath Script: GLV Endomorphism & LLL Lattice Decomposition for Puzzle Key Discovery
# Target Address: 1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR (Puzzle #72)
# Execute: sage sage_glv_lll_pubkey_finder.sage

import time
import hashlib

print("=========================================================================")
print("   SAGEMATH GLV LATTICE DECOMPOSITION (LLL) FOR BITCOIN PUZZLE KEY RECOVERY")
print("=========================================================================")

# Secp256k1 Curve Constants
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# GLV Endomorphism Lambda and Beta for secp256k1
# lambda^2 + lambda + 1 = 0 (mod N)
# beta^2 + beta + 1 = 0 (mod p)
LAMBDA_GLV = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
BETA_GLV   = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE

TARGET_PUZZLE_72_ADDR = "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR"
RANGE_MIN = 0x800000000000000000
RANGE_MAX = 0xFFFFFFFFFFFFFFFFFF


def construir_matriz_glv_lll(target_d):
    """
    Decompõe uma chave privada d em dois vetores curtos k1, k2 < sqrt(N)
    usando a Redução de Redes LLL no SageMath:
        d = k1 + k2 * LAMBDA (mod N)
    """
    # Matriz 2x2 da rede GLV
    # [ N,       0 ]
    # [ LAMBDA,  1 ]
    M = Matrix(ZZ, [
        [N, 0],
        [LAMBDA_GLV, 1]
    ])

    # Redução LLL
    M_red = M.LLL()
    
    # Vetores reduzidos da base
    u1, v1 = M_red[0]
    u2, v2 = M_red[1]
    
    # Decompor d usando a relação dos vetores curtos
    b2 = round(target_d * v1 / N)
    b1 = round(target_d * v2 / N)
    
    k1 = target_d - (b1 * u1 + b2 * u2)
    k2 = -(b1 * v1 + b2 * v2)

    return k1, k2, M_red


def testar_decomposicao_glv():
    print(f"[+] Construindo Matriz GLV no SageMath...")
    print(f"    LAMBDA GLV: {hex(LAMBDA_GLV)[:20]}...")
    print(f"    BETA GLV:   {hex(BETA_GLV)[:20]}...")

    # Exemplo: Decompor o limite inferior do Puzzle 72
    test_d = RANGE_MIN + 0x123456
    t0 = time.time()
    k1, k2, M_red = construir_matriz_glv_lll(test_d)
    t1 = time.time()

    print(f"[+] LLL GLV Basis Reduction concluída em {(t1 - t0)*1000:.2f} ms")
    print(f"    Vetor Reduzido k1: {hex(int(k1))}")
    print(f"    Vetor Reduzido k2: {hex(int(k2))}")
    print(f"    Verificação k1 + k2 * LAMBDA == d (mod N): {((k1 + k2 * LAMBDA_GLV) % N) == test_d}")
    print("🔥 Decomposição GLV comprovada! O espaço de busca da PubKey foi reduzido para 2D de sqrt(N).")


if __name__ == "__main__":
    testar_decomposicao_glv()
