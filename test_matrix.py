import random
from sympy import Matrix

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def test_hnp_leak(bits_leaked=64, num_signatures=5):
    print(f"\n=======================================================")
    print(f" TESTING HNP LLL: {bits_leaked} BITS LEAKED, {num_signatures} SIGNATURES")
    print(f"=======================================================")

    target_key = 0xabcdef1234567890abcdef1234567890
    X = N >> bits_leaked

    t_list = []
    u_list = []
    sigs = []

    for _ in range(num_signatures):
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

    m = num_signatures
    # Matrix construction:
    # Row 0..m-1: N on diag
    # Row m:     t_1, t_2, ..., t_m, 1, 0
    # Row m+1:   u_1, u_2, ..., u_m, 0, X
    rows = []
    for i in range(m):
        r = [0] * (m + 2)
        r[i] = N
        rows.append(r)
    
    rows.append(t_list + [1, 0])
    rows.append(u_list + [0, X])

    M = Matrix(rows)
    import time
    t0 = time.time()
    M_red = M.lll()
    t1 = time.time()

    print(f"[+] LLL Reduction completed in {(t1 - t0)*1000:.2f} ms")

    t0, u0 = t_list[0], u_list[0]
    t0_inv = pow(t0, -1, N)

    found = False
    for i in range(M_red.rows):
        row = [int(M_red[i, c]) for c in range(M_red.cols)]
        
        # Check k0 in row[0]
        for val in [row[0], -row[0], (row[0]) % N]:
            if 0 < val < X:
                cand_d = (t0_inv * (val - u0)) % N
                if cand_d == target_key:
                    print(f"🔥 SUCCESS! KEY RECOVERED in Row {i}: {hex(cand_d)}")
                    found = True
                    break
        if found:
            break

    if not found:
        print("❌ Key not recovered.")

if __name__ == "__main__":
    # Test 64 bits leak with 5 signatures (m * b = 320 > 256)
    test_hnp_leak(bits_leaked=64, num_signatures=5)
    # Test 32 bits leak with 9 signatures (m * b = 288 > 256)
    test_hnp_leak(bits_leaked=32, num_signatures=9)
