"""
Validação da Chave Pública e ECDSA do Puzzle #60
Public Key Alvo: 0348e843dc5b1bd246e6309b4924b81543d02b16c8083df973a89ce2c7eb89a10d
Range do Puzzle 60: [0x800000000000000 ... 0xfffffffffffffff] (2^59 .. 2^60-1)
"""

import ecdsa

# Parametros secp256k1
SECP256k1 = ecdsa.SECP256k1
N = SECP256k1.order
G = SECP256k1.generator

PUBKEY_ALVO_HEX = "0348e843dc5b1bd246e6309b4924b81543d02b16c8083df973a89ce2c7eb89a10d"


def testar_chave_privada(d_int: int) -> bool:
    """Verifica se d * G é igual à chave pública comprimida do Puzzle #60."""
    sk = ecdsa.SigningKey.from_secret_exponent(d_int, curve=SECP256k1)
    vk = sk.verifying_key
    pub_compressed = binascii.hexlify(vk.to_string("compressed")).decode('utf-8')
    return pub_compressed == PUBKEY_ALVO_HEX


def analisar_assinaturas_coletadas():
    r1 = 0xdf1cda1111b660c9f0235c0997f8120597a42565b2e2f84f8ee249e53207e6ce
    s1 = 0x66e5a17a6e457aafdbdc8961411fb167ac2473f08ecd85ed664af75648e2e3c5

    r2 = 0xb0d935af1a8b20186c2cd3e43dddb391d85acbfab890f025e683bc0da2534de7
    s2 = 0xb7816d64a59579da5328fbfd7ddd34b19ad864915fe2474338e53d04131257f

    r3 = 0xfd057986cf37b3eae6d0a165cb38ef66bfcb0c34ef7f59a15a9a8987bffdf3fe
    s3 = 0x14793550ea9369a710fd9e51f246a04e09f0cc59e3f6c1a9d314556430e7f6c4

    print("=========================================================================")
    print("   ANÁLISE DAS ASSINATURAS REAIS COLETADAS DA BLOCKCHAIN FOR PUZZLE #60")
    print("=========================================================================")
    print(f"[+] Assinatura 1 r: {hex(r1)}")
    print(f"[+] Assinatura 2 r: {hex(r2)}")
    print(f"[+] Assinatura 3 r: {hex(r3)}")

    # Verificar se houve reuso de r
    if r1 == r2 or r1 == r3 or r2 == r3:
        print("[!] REUSO DE NONCE DETECTADO!")
    else:
        print("[+] Nenhum reuso direto de r entre as 3 assinaturas.")

if __name__ == "__main__":
    import binascii
    analisar_assinaturas_coletadas()
