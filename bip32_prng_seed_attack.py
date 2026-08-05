"""
ATAQUE DE SEMENTE (SEED / BIP32 REVERSO / PRNG DISCOVERY) - BITCOIN PUZZLES
Autor: Antigravity AI Engine

Mecanismo:
  Testa múltiplos modelos determinísticos de geração de chaves privadas delimitadas por N bits:
    2^(N-1) <= d_N < 2^N

Validação estrita: exige acerto nos Puzzles de maior tamanho (#10, #20, #68, #69, #70).
"""

import sys
import hmac
import hashlib
import random
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Banco de dados de chaves resolvidas
SOLVED_KEYS = {
    1:  0x1,
    2:  0x3,
    3:  0x7,
    4:  0x8,
    5:  0x15,
    6:  0x31,
    7:  0x4c,
    8:  0xe0,
    9:  0x1d3,
    10: 0x202,
    11: 0x483,
    12: 0xa7b,
    13: 0x1460,
    14: 0x2930,
    15: 0x68f3,
    16: 0xc936,
    17: 0x1764f,
    18: 0x3080d,
    19: 0x57a9f,
    20: 0xd2c55,
    25: 0x1fa5ee5,
    30: 0x3d94cd64,
    35: 0x4aed21170,
    40: 0xe9ae4933d6,
    45: 0x122fca143c05,
    50: 0x22bd43c2e9354,
    55: 0x6abe1f9b67e114,
    60: 0xfc07a1825367bbe,
    61: 0x13c96a3742f64906,
    62: 0x363d541eb611abee,
    63: 0x7cce5efdaccf6808,
    64: 0xf7051f27b09112d4,
    65: 0x1a838b13505b26867,
    66: 0x2832ed74f2b5e35ee,
    67: 0x730fc235c1942c1ae,
    68: 0xbebb3940cd0fc1491,
    69: 0x101d83275fb2bc7e0c,
    70: 0x349b84b6431a6c4ef1,
}

TEST_PUZZLES_STRICT = [10, 15, 20, 60, 68, 69, 70]

def verificar_match_estrito(gerador_func, nome_modelo):
    """Verifica se uma função geradora recria as chaves conhecidas em puzzles de grande porte."""
    for n in TEST_PUZZLES_STRICT:
        try:
            cand = gerador_func(n)
            if cand != SOLVED_KEYS[n]:
                return False
        except Exception:
            return False
            
    print(f"\n🎉 [!!!] MODELO EXATO ENCONTRADO! {nome_modelo}")
    d71 = gerador_func(71)
    print(f"    🔥 CHAVE PRIVADA PUZZLE #71: {hex(d71)}")
    return True

# -------------------------------------------------------------------------
# MODELO 1: HMAC-SHA512 / HMAC-SHA256 (BIP32 Truncado)
# -------------------------------------------------------------------------
def testar_hmac_bip32_mask(seed_bytes: bytes, salt: bytes = b"Bitcoin seed"):
    def gen_sha512(n):
        min_n = 1 << (n - 1)
        span  = 1 << (n - 1)
        h = hmac.new(salt, seed_bytes + n.to_bytes(4, 'big'), hashlib.sha512).digest()
        val = int.from_bytes(h, 'big')
        return min_n + (val % span)
        
    def gen_sha256(n):
        min_n = 1 << (n - 1)
        span  = 1 << (n - 1)
        h = hmac.new(salt, seed_bytes + n.to_bytes(4, 'big'), hashlib.sha256).digest()
        val = int.from_bytes(h, 'big')
        return min_n + (val % span)

    if verificar_match_estrito(gen_sha512, f"HMAC-SHA512 (seed={seed_bytes.hex()})"):
        return True
    if verificar_match_estrito(gen_sha256, f"HMAC-SHA256 (seed={seed_bytes.hex()})"):
        return True
    return False

# -------------------------------------------------------------------------
# MODELO 2: Brainwallet SHA256(Passphrase + n)
# -------------------------------------------------------------------------
def testar_brainwallet_passphrase(passphrase: str):
    def gen_brain(n):
        min_n = 1 << (n - 1)
        span  = 1 << (n - 1)
        msg = f"{passphrase}_{n}".encode('utf-8')
        h = hashlib.sha256(msg).digest()
        val = int.from_bytes(h, 'big')
        return min_n + (val % span)
        
    def gen_brain_num(n):
        min_n = 1 << (n - 1)
        span  = 1 << (n - 1)
        msg = f"{passphrase}{n}".encode('utf-8')
        h = hashlib.sha256(msg).digest()
        val = int.from_bytes(h, 'big')
        return min_n + (val % span)

    if verificar_match_estrito(gen_brain, f"Brainwallet ('{passphrase}_N')"):
        return True
    if verificar_match_estrito(gen_brain_num, f"Brainwallet ('{passphrase}N')"):
        return True
    return False

# -------------------------------------------------------------------------
# MODELO 3: Python random.seed()
# -------------------------------------------------------------------------
def testar_python_random_seed(seed_val):
    def gen_py_random(n):
        min_n = 1 << (n - 1)
        max_n = (1 << n) - 1
        random.seed(f"{seed_val}_{n}")
        return random.randint(min_n, max_n)

    if verificar_match_estrito(gen_py_random, f"Python random.seed('{seed_val}_N')"):
        return True
    return False

def main():
    print("=" * 80)
    print("  ATAQUE DE SEMENTE / RECONSTRUÇÃO DE PRNG E BIP32 (VALIDAÇÃO ESTRITA)")
    print(f"  Testando modelos contra Puzzles de grande porte (#10, #20, #60, #68, #69, #70)...")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    palavras_semente = [
        "bitcoin", "satoshi", "nakamoto", "puzzle", "transaction", "secp256k1",
        "blockchain", "reward", "crypto", "challenge", "magic", "master", "secret",
        "privatekey", "71", "100", "2015", "january", "genesis", "block", "freedom",
        "proofofwork", "miner", "halving", "hodl", "peer2peer", "elliptic", "curve"
    ]

    print(f"\n[VETOR 1] Varrendo {len(palavras_semente)} sementes em palavras-chave...")
    encontrado = False

    for word in palavras_semente:
        if testar_hmac_bip32_mask(word.encode('utf-8')):
            encontrado = True
            break
        if testar_brainwallet_passphrase(word):
            encontrado = True
            break
        if testar_python_random_seed(word):
            encontrado = True
            break

    if not encontrado:
        print("\n[VETOR 2] Varrendo sementes numéricas de 0 a 10.000 (Validação Estrita)...")
        for num in range(10000):
            num_bytes = num.to_bytes(4, 'big')
            if testar_hmac_bip32_mask(num_bytes):
                encontrado = True
                break
            if testar_python_random_seed(num):
                encontrado = True
                break

    print("\n" + "=" * 80)
    if not encontrado:
        print("  [-] Nenhuma semente determinística simples ou BIP32 bateu com os Puzzles maiores.")
        print("  [-] O criador gerou cada chave usando entropia pseudoaleatória de alta qualidade.")
        print("  [+] Conclusão: A varredura de sub-ranges por GPU na ZONA 1 (via orquestrador aleatório) é a estratégia realista!")
    print("=" * 80)

if __name__ == "__main__":
    main()
