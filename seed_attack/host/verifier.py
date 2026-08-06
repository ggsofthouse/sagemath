"""
VERIFICADOR CRIPTOGRÁFICO DE ALTA PERFORMANCE (NATIVO COINCURVE C-ENGINE COM DUPLA DEDUÇÃO)
Autor: Antigravity AI Engine

Dupla Hipótese de Validação:
  1. Teste BIP32 Multi-Path (m/0/n, m/n, m/0'/n, m/44'/0'/0'/0/n) com máscara dos Puzzles #65-#70.
  2. Teste DIRETO de Chave Privada do Puzzle #71: (1 << 70) | (candidate & ((1 << 70) - 1)).
"""

import hmac
import hashlib

try:
    from coincurve import PrivateKey
    HAS_COINCURVE = True
except ImportError:
    HAS_COINCURVE = False

SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

KNOWN_PUZZLES = {
    65: 0x1a838b13505b26867,
    66: 0x2832ed74f2b5e35ee,
    67: 0x730fc235c1942c1ae,
    68: 0xbebb3940cd0fc1491,
    69: 0x101d83275fb2bc7e0c,
    70: 0x349b84b6431a6c4ef1,
}

TARGET_ADDRESS = "1PWo3Jeb9jrGwfHDNpdGK54CRas7fsVzXU"

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

def apply_puzzle_mask(raw_val: int, n: int) -> int:
    mask_bits = n - 1
    return (1 << mask_bits) | (raw_val & ((1 << mask_bits) - 1))

def privkey_to_pubkey_bytes(privkey_int: int) -> bytes:
    if HAS_COINCURVE:
        return PrivateKey((privkey_int % SECP256K1_N).to_bytes(32, 'big')).public_key.format(compressed=True)
    pt = point_mul(privkey_int % SECP256K1_N)
    prefix = b'\x02' if pt[1] % 2 == 0 else b'\x03'
    return prefix + pt[0].to_bytes(32, 'big')

def privkey_to_address_fast(privkey_int: int) -> str:
    pub_bytes = privkey_to_pubkey_bytes(privkey_int)
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

def derive_bip32_master(seed_bytes: bytes):
    h = hmac.new(b"Bitcoin seed", seed_bytes, hashlib.sha512).digest()
    master_priv = int.from_bytes(h[:32], 'big') % SECP256K1_N
    return master_priv, h[32:]

def derive_unhardened_child(master_priv: int, master_chain: bytes, index: int):
    pub_bytes = privkey_to_pubkey_bytes(master_priv)
    msg = pub_bytes + index.to_bytes(4, 'big')
    h = hmac.new(master_chain, msg, hashlib.sha512).digest()
    child_priv = (int.from_bytes(h[:32], 'big') + master_priv) % SECP256K1_N
    return child_priv

def verify_full_seed(seed_input, known_db=None) -> bool:
    """Verifica semente testando BIP32 Multi-Path E Chave Privada Direta do Puzzle #71."""
    if isinstance(seed_input, int):
        seed_bytes = seed_input.to_bytes(8, 'big')
        raw_int = seed_input
    elif isinstance(seed_input, bytes):
        seed_bytes = seed_input
        raw_int = int.from_bytes(seed_input, 'big')
    else:
        seed_bytes = seed_input.encode('utf-8')
        raw_int = int.from_bytes(hashlib.sha256(seed_bytes).digest(), 'big')

    # HIPÓTESE A: TESTE DIRETO DE CHAVE PRIVADA DO PUZZLE #71
    try:
        direct_priv71 = apply_puzzle_mask(raw_int, 71)
        if privkey_to_address_fast(direct_priv71) == TARGET_ADDRESS:
            print(f"\n🎉🎉🎉 CONFIRMAÇÃO TOTAL POR CHAVE DIRETA! 🎉🎉🎉")
            print(f"🔥 CHAVE PRIVADA PUZZLE #71: {hex(direct_priv71)}")
            print(f"🏆 ENDEREÇO BITCOIN CONFIRMADO 100%: {TARGET_ADDRESS}")
            return True
    except Exception:
        pass

    # HIPÓTESE B: DERIVAÇÃO BIP32 MULTI-PATH
    try:
        master_priv, master_chain = derive_bip32_master(seed_bytes)
    except Exception:
        return False

    paths = [
        [0],                     # m/0/n (Electrum / BIP32)
        [],                      # m/n
        [0x80000000],            # m/0'/n
        [0x80000000 + 44, 0x80000000, 0x80000000, 0] # m/44'/0'/0'/0/n
    ]

    for p in paths:
        curr_priv = master_priv
        curr_chain = master_chain
        
        for idx in p:
            if idx >= 0x80000000:
                msg = b'\x00' + curr_priv.to_bytes(32, 'big') + idx.to_bytes(4, 'big')
            else:
                pub = privkey_to_pubkey_bytes(curr_priv)
                msg = pub + idx.to_bytes(4, 'big')
            h = hmac.new(curr_chain, msg, hashlib.sha512).digest()
            curr_priv = (int.from_bytes(h[:32], 'big') + curr_priv) % SECP256K1_N
            curr_chain = h[32:]

        # SHORT-CIRCUIT AGRESSIVO no PUZZLE #70!
        child70_raw = derive_unhardened_child(curr_priv, curr_chain, 70)
        child70_masked = apply_puzzle_mask(child70_raw, 70)

        if child70_masked != KNOWN_PUZZLES[70]:
            continue

        # Valida os anteriores (#65 a #69)
        valid = True
        for n in range(65, 70):
            child_raw = derive_unhardened_child(curr_priv, curr_chain, n)
            if apply_puzzle_mask(child_raw, n) != KNOWN_PUZZLES[n]:
                valid = False
                break

        if valid:
            child71_raw = derive_unhardened_child(curr_priv, curr_chain, 71)
            priv71 = apply_puzzle_mask(child71_raw, 71)
            addr71 = privkey_to_address_fast(priv71)

            if addr71 == TARGET_ADDRESS:
                print(f"\n🎉🎉🎉 CONFIRMAÇÃO TOTAL BIP32 NO HOST CPU! 🎉🎉🎉")
                print(f"🔥 CHAVE PRIVADA PUZZLE #71: {hex(priv71)}")
                print(f"🏆 ENDEREÇO BITCOIN CONFIRMADO 100%: {addr71}")
                return True
    return False
