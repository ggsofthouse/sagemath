"""
HNP (Hidden Number Problem) Solver with Correct Column Scaling
Demonstrates exact LLL lattice reduction key recovery for secp256k1.
"""

import random
import time
from sympy import Matrix

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def test_scaled_hnp(leak_bits=32, num_signatures=10):
    print("=========================================================================")
    print(f"[+] ATTACK TEST: {leak_bits} bits leaked per nonce | {num_signatures} signatures")
    print("=========================================================================")

    target_key = 0xabcdef1234567890abcdef1234567890
    print(f"[+] Target Key: {hex(target_key)}")

    X = N >> leak_bits
    m = num_signatures

    t_list = []
    u_list = []
    sigs = []

    for _ in range(m):
        k = random.randint(1, X)
        z = random.randint(1, N - 1)
        r = random.randint(1, N - 1)
        s = (pow(k, -1, N) * (z + r * target_key)) % N

        s_inv = pow(s, -1, N)
        t = (s_inv * r) % N
        u = (s_inv * z) % N
        t_list.append(t)
        u_list.append(u)
        sigs.append((k, r, s, z))

    # Scale factor for column m (d)
    # Multiply all columns except column m by 2^(leak_bits)
    scale = 1 << leak_bits

    rows = []
    for i in range(m):
        r = [0] * (m + 2)
        r[i] = N * scale
        rows.append(r)

    rows.append([t * scale for t in t_list] + [1, 0])
    rows.append([u * scale for u in u_list] + [0, X * scale])

    M = Matrix(rows)

    t0 = time.time()
    M_red = M.lll()
    t1 = time.time()

    print(f"[+] LLL basis reduction completed in {(t1 - t0)*1000:.2f} ms")

    # Extract private key from column m of reduced rows
    recovered = False
    for i in range(M_red.rows):
        cand_d1 = int(M_red[i, m]) % N
        cand_d2 = int(-M_red[i, m]) % N

        for cand in [cand_d1, cand_d2]:
            if cand == target_key:
                print(f"[SUCCESS] Private key RECOVERED in Row {i} column {m}:")
                print(f"          {hex(cand)}")
                recovered = True
                break
        if recovered:
            break

    if not recovered:
        print("[FAIL] Key not found in reduced basis.")

    return recovered


if __name__ == "__main__":
    # Test 1: 64 bits leaked (4 signatures)
    test_scaled_hnp(leak_bits=64, num_signatures=4)
    # Test 2: 32 bits leaked (10 signatures)
    test_scaled_hnp(leak_bits=32, num_signatures=10)
    # Test 3: 16 bits leaked (18 signatures)
    test_scaled_hnp(leak_bits=16, num_signatures=18)
