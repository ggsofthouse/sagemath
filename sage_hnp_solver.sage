# SageMath Script: HNP Key Recovery via LLL (Kannan's Embedding)
# Execute in SageMath: sage sage_hnp_solver.sage
# Or copy-paste into SageMathCell (https://sagecell.sagemath.org)

import random
import time

print("===============================================================")
print("   SAGEMATH HNP (HIDDEN NUMBER PROBLEM) LLL ATTACK SIMULATION  ")
print("===============================================================")

# 1. Secp256k1 Curve Order N
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
E = SmallLemma = None

def run_hnp_attack(bits_leaked=8, num_signatures=6):
    """
    Simulates ECDSA signatures with 'bits_leaked' known MSB zeros in nonce 'k'.
    Constructs the lattice matrix M and runs LLL to find the private key 'd'.
    """
    print(f"\n[+] Running Attack with {bits_leaked} bits leaked per nonce, using {num_signatures} signatures...")

    # Generate a target secret private key d
    CHAVE_PRIVADA_ALVO = random.randint(1, N - 1)
    print(f"[+] Private Key to Recover: {hex(CHAVE_PRIVADA_ALVO)}")

    # Upper bound X for nonces k_i < X
    X = N >> bits_leaked

    # Collect signatures (r_i, s_i, z_i)
    t_list = []
    u_list = []
    signatures = []

    for i in range(num_signatures):
        k = random.randint(1, X)
        z = random.randint(1, N - 1)
        r = random.randint(1, N - 1)
        s = (pow(k, -1, N) * (z + r * CHAVE_PRIVADA_ALVO)) % N

        s_inv = pow(s, -1, N)
        t = (s_inv * r) % N
        u = (s_inv * z) % N

        t_list.append(t)
        u_list.append(u)
        signatures.append((r, s, z, k))

    # 2. CONSTRUCT KANNAN EMBEDDING LATTICE MATRIX (m+2) x (m+2)
    # Row vectors structure:
    # Row 0..m-1: [N, 0, ..., 0, 0, 0]
    # Row m:     [t_1, t_2, ..., t_m, X/N, 0]
    # Row m+1:   [u_1, u_2, ..., u_m, 0, X]

    m = num_signatures
    scale_d = max(1, X // N)

    matrix_rows = []
    for i in range(m):
        row = [0] * (m + 2)
        row[i] = N
        matrix_rows.append(row)

    # Row m (t vector)
    matrix_rows.append(t_list + [scale_d, 0])
    # Row m+1 (u vector)
    matrix_rows.append(u_list + [0, X])

    M = Matrix(ZZ, matrix_rows)

    print("\n[+] Kannan Embedding Matrix M created (dimension %d x %d)" % (M.nrows(), M.ncols()))

    # 3. RUN LLL BASIS REDUCTION
    t_start = time.time()
    M_reduced = M.LLL()
    t_end = time.time()

    print(f"[+] LLL Reduction completed in {(t_end - t_start)*1000:.2f} ms")

    # 4. EXTRACT PRIVATE KEY FROM REDUCED BASIS
    # Look for vector where last component is +/- X or corresponding k_i bounds
    recovered_key = None

    t0, u0 = t_list[0], u_list[0]
    t0_inv = pow(t0, -1, N)

    for row in M_reduced:
        # Candidate k0 is row[0]
        for cand_k0 in [int(row[0]), int(-row[0]), int(row[0]) % N]:
            if 0 < cand_k0 < X:
                cand_d = (t0_inv * (cand_k0 - u0)) % N
                if cand_d == CHAVE_PRIVADA_ALVO:
                    recovered_key = cand_d
                    break
        if recovered_key:
            break

    if recovered_key == CHAVE_PRIVADA_ALVO:
        print(f"[SUCCESS] Private Key RECOVERED: {hex(recovered_key)}")
        return True
    else:
        print("[FAIL] Key not found in reduced vector basis.")
        return False

if __name__ == "__main__":
    run_hnp_attack(bits_leaked=8, num_signatures=6)
