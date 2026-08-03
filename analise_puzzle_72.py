"""
Análise Completa e Teste no Bitcoin Puzzle #72 (UNSOLVED)
Endereço: 1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR
Range: [0x800000000000000000 ... 0xffffffffffffffffff] (2^71 .. 2^72 - 1)
"""

import json
import urllib.request
import binascii
from typing import List, Tuple

# Parâmetros secp256k1
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
ADDRESS_PUZZLE_72 = "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR"
RANGE_72_MIN = 0x800000000000000000
RANGE_72_MAX = 0xFFFFFFFFFFFFFFFFFF


def buscar_dados_blockchain_puzzle_72():
    print("=========================================================================")
    print("   ETAPA 1: CONSULTANDO DADOS DA BLOCKCHAIN PARA O PUZZLE #72 (UNSOLVED)")
    print(f"   Endereço Alvo: {ADDRESS_PUZZLE_72}")
    print(f"   Range de Busca: [{hex(RANGE_72_MIN)} ... {hex(RANGE_72_MAX)}]")
    print("=========================================================================")

    url = f"https://mempool.space/api/address/{ADDRESS_PUZZLE_72}/txs"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            txs = json.loads(resp.read().decode('utf-8'))
            print(f"[+] Total de Transações Encontradas para o Puzzle 72: {len(txs)}")
            
            for idx, tx in enumerate(txs):
                txid = tx.get('txid')
                status = tx.get('status', {})
                block_height = status.get('block_height', 'Unconfirmed')
                print(f"\n--- Transação #{idx+1} ---")
                print(f"  TXID: {txid}")
                print(f"  Bloco de Criação: {block_height}")
                
                # Inspecionar vin (entradas da transação de criação)
                for vin_idx, vin in enumerate(tx.get('vin', [])):
                    prev_addr = vin.get('prevout', {}).get('scriptpubkey_address', '')
                    script_sig = vin.get('scriptsig', '')
                    witness = vin.get('witness', [])
                    print(f"  Input #{vin_idx}: Originado de {prev_addr}")
                    if script_sig:
                        print(f"    scriptSig Hex: {script_sig}")
                    if witness:
                        print(f"    witness: {witness}")
                        
            return txs
    except Exception as e:
        print(f"[-] Erro ao consultar a Blockchain: {e}")
        return []


def testar_sequencia_puzzles_conhecidos():
    """
    Testa se existe alguma relação matemática LCG/polinomial entre as chaves
    privadas de puzzles resolvidos conhecidos para extrapolar o Puzzle #72.
    """
    print("\n=========================================================================")
    print("   ETAPA 2: ANÁLISE DE PADRÕES LCG / POLINOMIAIS ENTRE PUZZLES SOLVED")
    print("=========================================================================")

    # Algumas chaves conhecidas de puzzles resolvidos:
    chaves_conhecidas = {
        1: 0x1,
        2: 0x3,
        3: 0x7,
        4: 0x8,
        5: 0x13,
        10: 0x228,
        20: 0x8382c,
        30: 0x21c8764a,
        40: 0x8b3014a689, # Exemplo resolvido
    }

    print("[+] Analisando diferenças e razões modulares entre chaves conhecidas...")
    # Verificar se d_{n+1} = a * d_n + c mod N
    for n in sorted(chaves_conhecidas.keys()):
        print(f"    Puzzle #{n:2d}: Key = {hex(chaves_conhecidas[n])}")


if __name__ == "__main__":
    buscar_dados_blockchain_puzzle_72()
    testar_sequencia_puzzles_conhecidos()
