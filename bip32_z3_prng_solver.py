"""
SISTEMA AVANÇADO DE RECONSTRUÇÃO Z3 SMT SOLVER - PUZZLE BITCOIN
Autor: Antigravity AI Engine

Melhorias:
  1. Timeout configurável de 60 segundos por modelo.
  2. Suporte a BitVecs de 64, 128 e 256 bits para as variáveis LCG (A, C, M).
  3. Restrição de M a potências de 2 (2^32, 2^48, 2^64, 2^128, 2^256).
  4. Validação estrita acumulada e validação cruzada completa contra os Puzzles #65 a #70.
  5. Verificação final de endereço Bitcoin P2PKH (1PWo3Jeb9jrGwfHDNpdGK54CRas7fsVzXU).
"""

import os
import sys
import z3
import hashlib
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

TARGET_ADDRESS = "1PWo3Jeb9jrGwfHDNpdGK54CRas7fsVzXU"

SOLVED_KEYS = {
    65: 0x1a838b13505b26867,
    66: 0x2832ed74f2b5e35ee,
    67: 0x730fc235c1942c1ae,
    68: 0xbebb3940cd0fc1491,
    69: 0x101d83275fb2bc7e0c,
    70: 0x349b84b6431a6c4ef1,
}

TEST_PUZZLES = [65, 66, 67, 68, 69, 70]

def point_add(p1, p2):
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 != y2: return None
    if x1 == x2:
        l = (3 * x1 * x1) * pow(2 * y1, P - 2, P) % P
    else:
        l = (y2 - y1) * pow(x2 - x1, P - 2, P) % P
    x3 = (l * l - x1 - x2) % P
    y3 = (l * (x1 - x3) - y1) % P
    return (x3, y3)

def point_mul(k, p=G):
    r = None
    q = p
    while k > 0:
        if k & 1: r = point_add(r, q)
        q = point_add(q, q)
        k >>= 1
    return r

def privkey_to_address(privkey_int: int) -> str:
    pt = point_mul(privkey_int)
    prefix = b'\x02' if pt[1] % 2 == 0 else b'\x03'
    pub_bytes = prefix + pt[0].to_bytes(32, 'big')
    sha = hashlib.sha256(pub_bytes).digest()
    rip = hashlib.new('ripemd160', sha).digest()
    ext = b'\x00' + rip
    chk = hashlib.sha256(hashlib.sha256(ext).digest())[:4]
    alpha = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(ext + chk, 'big')
    res = ''
    while num > 0:
        num, r = divmod(num, 58)
        res = alpha[r] + res
    for b in ext + chk:
        if b == 0: res = '1' + res
        else: break
    return res

def testar_z3_bits(bit_width: int, timeout_ms: int = 60000) -> bool:
    print(f"\n  [+] Executando Z3 SMT Solver com BitVec de {bit_width} bits (Timeout: {timeout_ms/1000:.0f}s)...")
    solver = z3.Solver()
    solver.set("timeout", timeout_ms)

    A = z3.BitVec('A', bit_width)
    C = z3.BitVec('C', bit_width)
    M = z3.BitVec('M', bit_width)

    # Restrições de M como potências de 2 comuns em PRNGs (2^32, 2^48, 2^64, 2^128, 2^256)
    potencias_m = [z3.BitVecVal(1 << exp, bit_width) for exp in [32, 48, 64, 128, 256] if exp <= bit_width]
    if potencias_m:
        solver.add(z3.Or([M == p_val for p_val in potencias_m]))

    solver.add(M > 1)
    solver.add(A > 1)

    vals_masked = {n: SOLVED_KEYS[n] - (1 << (n - 1)) for n in TEST_PUZZLES}
    
    for i in range(len(TEST_PUZZLES) - 1):
        n1 = TEST_PUZZLES[i]
        n2 = TEST_PUZZLES[i + 1]
        v1 = z3.BitVecVal(vals_masked[n1], bit_width)
        v2 = z3.BitVecVal(vals_masked[n2], bit_width)
        solver.add((A * v1 + C) % M == v2)

    res = solver.check()
    if res == z3.sat:
        model = solver.model()
        a_val = model[A].as_long()
        c_val = model[C].as_long()
        m_val = model[M].as_long()
        print(f"\n🎉🎉🎉 Z3 SOLVER ENCONTROU MODELO! ({bit_width} bits) 🎉🎉🎉")
        print(f"  A = {hex(a_val)}")
        print(f"  C = {hex(c_val)}")
        print(f"  M = {hex(m_val)}")

        # Validação cruzada estrita contra todos os puzzles de controle
        cross_valid = True
        for i in range(len(TEST_PUZZLES) - 1):
            n1 = TEST_PUZZLES[i]
            n2 = TEST_PUZZLES[i + 1]
            if (a_val * vals_masked[n1] + c_val) % m_val != vals_masked[n2]:
                cross_valid = False
                break

        if not cross_valid:
            print("  [!] Modelo encontrado mas NÃO passou na validação cruzada estrita.")
            return False

        print("  [OK] Modelo validado 100% em validação cruzada contra todos os puzzles anteriores!")

        # Extrapolar para o Puzzle #71
        v70_raw = vals_masked[70]
        v71_raw = (a_val * v70_raw + c_val) % m_val
        d71 = (1 << 70) + v71_raw
        addr71 = privkey_to_address(d71)

        print(f"🔥 CHAVE PRIVADA PUZZLE #71: {hex(d71)}")
        print(f"  Endereço Bitcoin Derivado : {addr71}")
        print(f"  Endereço Alvo Esperado     : {TARGET_ADDRESS}")

        if addr71 == TARGET_ADDRESS:
            print("  🏆 ENDEREÇO BITCOIN CONFIRMADO 100% COM SUCESSO!")
            return True
    else:
        print(f"  [-] Z3 Solver ({bit_width} bits): Nenhum modelo encontrado ({res}).")
    return False

def main():
    print("=" * 80)
    print(" 🧠 Z3 SMT SOLVER OTIMIZADO - PUZZLE BITCOIN (64, 128, 256 BITS)")
    print(f"  Alvo: {TARGET_ADDRESS}")
    print(f"  Puzzles de Controle: {TEST_PUZZLES}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    for bw in [64, 128, 256]:
        if testar_z3_bits(bw, timeout_ms=60000):
            break

    print("\n" + "=" * 80)
    print("  [FIM DE ANÁLISE Z3 SOLVER]")
    print("=" * 80)

if __name__ == "__main__":
    main()
