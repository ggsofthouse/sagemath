"""
HNP (Hidden Number Problem) Solver via LLL Lattice Reduction (SymPy / SageMath compatible)
Author: Antigravity AI Engine

This module implements Kannan's Embedding Lattice Reduction (LLL) to extract
Bitcoin secp256k1 private keys from ECDSA signatures with leaked or biased nonces.

Mathematical Bound Rule:
For LLL to recover the private key, the total leaked bits across all signatures
must exceed the order size (256 bits):
    (Number of Signatures 'm') * (Leaked Bits per Nonce 'b') > 256
"""

import random
import time
from typing import List, Tuple, Optional
from sympy import Matrix

# Secp256k1 Elliptic Curve Order N
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def build_kannan_hnp_matrix(signatures: List[Tuple[int, int, int]], bounds_x: int) -> Matrix:
    """
    Constructs the (m+2) x (m+2) Kannan's Embedding Matrix for the Hidden Number Problem.

    signatures: List of tuples (r, s, z)
    bounds_x: Upper bound for nonces k_i < bounds_x (e.g. N >> leak_bits)
    """
    m = len(signatures)
    t_list = []
    u_list = []

    for r, s, z in signatures:
        s_inv = pow(s, -1, N)
        t = (s_inv * r) % N
        u = (s_inv * z) % N
        t_list.append(t)
        u_list.append(u)

    # Initialize (m+2) x (m+2) integer matrix
    rows = []
    for i in range(m):
        row = [0] * (m + 2)
        row[i] = N
        rows.append(row)

    # Row m: [t_1, t_2, ..., t_m, 1, 0]
    rows.append(t_list + [1, 0])

    # Row m+1: [u_1, u_2, ..., u_m, 0, bounds_x]
    rows.append(u_list + [0, bounds_x])

    return Matrix(rows)


def recover_private_key_hnp(signatures: List[Tuple[int, int, int]], bounds_x: int) -> Optional[int]:
    """
    Performs LLL reduction on the Kannan embedding matrix and extracts the private key 'd'.
    """
    matrix = build_kannan_hnp_matrix(signatures, bounds_x)
    reduced = matrix.lll()

    r0, s0, z0 = signatures[0]
    s0_inv = pow(s0, -1, N)
    t0 = (s0_inv * r0) % N
    u0 = (s0_inv * z0) % N
    t0_inv = pow(t0, -1, N)

    for row_idx in range(reduced.rows):
        row = [int(reduced[row_idx, c]) for c in range(reduced.cols)]

        # Check candidate k0 in row[0]
        for val in [row[0], -row[0], row[0] % N]:
            if 0 < val < bounds_x:
                cand_d = (t0_inv * (val - u0)) % N
                # Verification: verify against all signatures
                valid = True
                for r, s, z in signatures:
                    chk_k = (pow(s, -1, N) * (z + r * cand_d)) % N
                    if chk_k >= bounds_x or chk_k <= 0:
                        valid = False
                        break
                if valid:
                    return cand_d

    return None


def run_hnp_simulation(leak_bits: int = 64, num_signatures: int = 5):
    """
    Simulates ECDSA signature generation with specified nonce bit leakage,
    and runs the LLL reduction attack to recover the exact private key.
    """
    required_sigs = (256 // leak_bits) + 1
    print("=========================================================================")
    print(f"=== HNP LLL ATTACK SIMULATION ({leak_bits} BITS LEAKED PER NONCE) ===")
    print("=========================================================================")
    print(f"[+] Theoretical requirement: m * b > 256 bits (Minimum signatures needed: {required_sigs})")
    print(f"[+] Using {num_signatures} signatures for LLL matrix...")

    # Generate random target key
    target_private_key = random.randint(1, N - 1)
    print(f"[+] Target Private Key (Hex): {hex(target_private_key)}")

    # Upper bound for nonces k < X
    bounds_x = N >> leak_bits

    # Simulate ECDSA signatures (r, s, z)
    signatures = []
    for i in range(num_signatures):
        k = random.randint(1, bounds_x)
        z = random.randint(1, N - 1)
        r = random.randint(1, N - 1)
        s = (pow(k, -1, N) * (z + r * target_private_key)) % N
        signatures.append((r, s, z))

    # Run LLL attack
    t0 = time.time()
    recovered_key = recover_private_key_hnp(signatures, bounds_x)
    t1 = time.time()

    if recovered_key == target_private_key:
        print(f"[SUCCESS] Private Key RECOVERED in {(t1 - t0)*1000:.2f} milliseconds!")
        print(f"[+] Recovered Key: {hex(recovered_key)}")
        return True
    else:
        print("[FAIL] Key not recovered. Try increasing the number of signatures.")
        return False


if __name__ == "__main__":
    # Example 1: 64 bits leaked with 5 signatures
    run_hnp_simulation(leak_bits=64, num_signatures=5)
    # Example 2: 32 bits leaked with 9 signatures
    run_hnp_simulation(leak_bits=32, num_signatures=9)
