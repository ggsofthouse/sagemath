import random
import time
from fractions import Fraction
from typing import List

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def exact_lll(basis: List[List[int]], delta: Fraction = Fraction(3, 4)) -> List[List[int]]:
    """
    Exact Rational LLL Basis Reduction in Pure Python (Arbitrary Precision).
    Uses fractions.Fraction for 100% exact Gram-Schmidt projection without float error.
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
                # Nearest integer
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


def test_hnp_exact(leak_bits=64, num_signatures=5):
    print("=========================================================================")
    print(f"[+] HNP EXACT RATIONAL LLL: {leak_bits} bits leaked | {num_signatures} signatures")
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

    scale = 1 << leak_bits

    rows = []
    for i in range(m):
        r = [0] * (m + 2)
        r[i] = N * scale
        rows.append(r)

    rows.append([t * scale for t in t_list] + [1, 0])
    rows.append([u * scale for u in u_list] + [0, X * scale])

    t0 = time.time()
    B_red = exact_lll(rows)
    t1 = time.time()

    print(f"[+] Exact LLL reduction completed in {(t1 - t0)*1000:.2f} ms")

    recovered = False
    for i in range(len(B_red)):
        cand_d1 = int(B_red[i][m]) % N
        cand_d2 = int(-B_red[i][m]) % N

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
    test_hnp_exact(leak_bits=64, num_signatures=5)
