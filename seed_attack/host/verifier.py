"""
VERIFICADOR DE HIT & APLICAÇÃO DE MÁSCARA DO PUZZLE (HOST CPU - MULTI-PATH BIP32 & INT/BYTES)
Autor: Antigravity AI Engine
"""

import hmac
import hashlib

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

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

def privkey_to_pubkey_bytes(privkey_int: int) -> bytes:
    """Retorna os 33 bytes da Chave Pública Comprimida (0x02/0x03 + X)."""
    pt = point_mul(privkey_int)
    prefix = b'\x02' if pt[1] % 2 == 0 else b'\x03'
    return prefix + pt[0].to_bytes(32, 'big')

def privkey_to_address(privkey_int: int) -> str:
    """Deriva o Endereço Bitcoin P2PKH da chave privada."""
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

def derive_bip32_master(seed_bytes: bytes) -> tuple:
    I = hmac.new(b"Bitcoin seed", seed_bytes, hashlib.sha512).digest()
    master_privkey = int.from_bytes(I[:32], 'big') % N
    chain_code = I[32:]
    return master_privkey, chain_code

def derive_bip32_child(parent_privkey: int, parent_chain: bytes, index: int, hardened: bool = False) -> tuple:
    if hardened:
        index += 0x80000000
        data = b'\x00' + parent_privkey.to_bytes(32, 'big') + index.to_bytes(4, 'big')
    else:
        parent_pub_bytes = privkey_to_pubkey_bytes(parent_privkey) # 33 bytes!
        data = parent_pub_bytes + index.to_bytes(4, 'big')

    I = hmac.new(parent_chain, data, hashlib.sha512).digest()
    IL = int.from_bytes(I[:32], 'big')
    child_privkey = (IL + parent_privkey) % N
    child_chain = I[32:]
    return child_privkey, child_chain

def derive_by_path(m_priv, m_chain, n, path_type="m/n"):
    """Deriva a chave filha segundo o path escolhido."""
    if path_type == "m/n":
        child, _ = derive_bip32_child(m_priv, m_chain, n, hardened=False)
        return child

    if path_type == "m/0/n":
        p1, c1 = derive_bip32_child(m_priv, m_chain, 0, hardened=False)
        child, _ = derive_bip32_child(p1, c1, n, hardened=False)
        return child

    if path_type == "m/0'/n":
        p1, c1 = derive_bip32_child(m_priv, m_chain, 0, hardened=True)
        child, _ = derive_bip32_child(p1, c1, n, hardened=False)
        return child

    if path_type == "m/44'/0'/0'/0/n":
        p1, c1 = derive_bip32_child(m_priv, m_chain, 44, hardened=True)
        p2, c2 = derive_bip32_child(p1, c1, 0, hardened=True)
        p3, c3 = derive_bip32_child(p2, c2, 0, hardened=True)
        p4, c4 = derive_bip32_child(p3, c3, 0, hardened=False)
        child, _ = derive_bip32_child(p4, c4, n, hardened=False)
        return child

    # fallback
    child, _ = derive_bip32_child(m_priv, m_chain, n, hardened=False)
    return child

def apply_puzzle_mask(raw_key: int, n: int) -> int:
    min_n = 1 << (n - 1)
    span  = 1 << (n - 1)
    return min_n + (raw_key % span)

def verify_full_seed(seed_val, known_keys_db: dict) -> bool:
    """
    Testa a semente em vários paths BIP32.
    Aceita seed_val como int ou bytes.
    """
    if isinstance(seed_val, int):
        seed_bytes = seed_val.to_bytes(8, 'big')
    elif isinstance(seed_val, bytes):
        seed_bytes = seed_val  # já é bytes (ex: SHA256)
    elif isinstance(seed_val, str):
        seed_bytes = seed_val.encode('utf-8')
    else:
        return False

    m_priv, m_chain = derive_bip32_master(seed_bytes)

    paths = ["m/n", "m/0/n", "m/0'/n", "m/44'/0'/0'/0/n"]

    for path in paths:
        ok = True
        for n_str, hex_expected in known_keys_db.get("keys", {}).items():
            n = int(n_str)
            expected = int(hex_expected, 16)
            child_priv = derive_by_path(m_priv, m_chain, n, path)
            cand = apply_puzzle_mask(child_priv, n)
            if cand != expected:
                ok = False
                break

        if not ok:
            continue

        # Passou em todas as chaves conhecidas neste path → gera #71
        child_71 = derive_by_path(m_priv, m_chain, 71, path)
        d71 = apply_puzzle_mask(child_71, 71)
        addr71 = privkey_to_address(d71)

        print(f"\n🎉 HIT CONFIRMADO NO PATH: {path}")
        print(f"  Semente : {seed_val}")
        print(f"  Privkey #71 : {hex(d71)}")
        print(f"  Endereço    : {addr71}")
        print(f"  Alvo        : {TARGET_ADDRESS}")

        if addr71 == TARGET_ADDRESS:
            print("  🏆 ENDEREÇO CONFIRMADO!")
            return True

    return False
