"""
VERIFICADOR DE HIT & APLICAÇÃO DE MÁSCARA DO PUZZLE (HOST CPU)
Autor: Antigravity AI Engine
"""

import hmac
import hashlib

SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def derive_bip32_master(seed_bytes: bytes) -> tuple:
    I = hmac.new(b"Bitcoin seed", seed_bytes, hashlib.sha512).digest()
    master_privkey = int.from_bytes(I[:32], 'big') % SECP256K1_ORDER
    chain_code = I[32:]
    return master_privkey, chain_code

def derive_child_privkey(parent_privkey: int, parent_chain: bytes, index: int) -> tuple:
    data = parent_privkey.to_bytes(32, 'big') + index.to_bytes(4, 'big')
    I = hmac.new(parent_chain, data, hashlib.sha512).digest()
    IL = int.from_bytes(I[:32], 'big')
    child_privkey = (IL + parent_privkey) % SECP256K1_ORDER
    child_chain = I[32:]
    return child_privkey, child_chain

def apply_puzzle_mask(raw_key: int, n: int) -> int:
    """Aplica a máscara exata do puzzle: 2^(n-1) + (raw_key mod 2^(n-1))"""
    min_n = 1 << (n - 1)
    span  = 1 << (n - 1)
    return min_n + (raw_key % span)

def verify_full_seed(seed_val: int, known_keys_db: dict) -> bool:
    """Confirmação estrita de acerto no CPU para evitar falsos positivos."""
    seed_bytes = seed_val.to_bytes(8, 'big')
    m_priv, m_chain = derive_bip32_master(seed_bytes)
    
    for n_str, hex_expected in known_keys_db.get("keys", {}).items():
        n = int(n_str)
        expected = int(hex_expected, 16)
        child_priv, _ = derive_child_privkey(m_priv, m_chain, n)
        cand = apply_puzzle_mask(child_priv, n)
        if cand != expected:
            return False
            
    # Se passou em todas as chaves conhecidas, calcula Puzzle #71!
    child_71, _ = derive_child_privkey(m_priv, m_chain, 71)
    d71 = apply_puzzle_mask(child_71, 71)
    print(f"\n🎉🎉🎉 CONFIRMAÇÃO TOTAL NO HOST CPU! SEMENTE: {seed_val} 🎉🎉🎉")
    print(f"🔥 CHAVE PRIVADA PUZZLE #71: {hex(d71)}")
    return True
