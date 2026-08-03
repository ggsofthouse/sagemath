"""
Análise Real do Bitcoin Puzzle #60
Endereço: 1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su
Public Key: 0348e843dc5b1bd246e6309b4924b81543d02b16c8083df973a89ce2c7eb89a10d

Este script conecta à API da Blockchain e obtém os dados reais do Puzzle #60.
"""

import json
import urllib.request
import binascii

# Parâmetros secp256k1
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
ADDRESS_PUZZLE_60 = "1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su"
PUBKEY_PUZZLE_60 = "0348e843dc5b1bd246e6309b4924b81543d02b16c8083df973a89ce2c7eb89a10d"
RANGE_MIN = 0x800000000000000
RANGE_MAX = 0xFFFFFFFFFFFFFFF


def buscar_transacoes_puzzle():
    print("=========================================================================")
    print("   ETAPA 1: BUSCANDO TRANSAÇÕES REAIS DO PUZZLE #60 NA BLOCKCHAIN")
    print(f"   Endereço: {ADDRESS_PUZZLE_60}")
    print(f"   PubKey:   {PUBKEY_PUZZLE_60}")
    print(f"   Range:    [{hex(RANGE_MIN)} ... {hex(RANGE_MAX)}]")
    print("=========================================================================")

    url = f"https://mempool.space/api/address/{ADDRESS_PUZZLE_60}/txs"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[+] Total de Transações Encontradas na Blockchain: {len(data)}")
            
            for idx, tx in enumerate(data):
                txid = tx.get('txid')
                vin_count = len(tx.get('vin', []))
                vout_count = len(tx.get('vout', []))
                status = tx.get('status', {})
                block_height = status.get('block_height', 'Unconfirmed')
                
                print(f"\n--- Transação #{idx+1} ---")
                print(f"  TXID: {txid}")
                print(f"  Bloco: {block_height}")
                print(f"  Entradas (inputs): {vin_count} | Saídas (outputs): {vout_count}")
                
                # Inspecionar vin scriptWitness / scriptSig
                for vin_idx, vin in enumerate(tx.get('vin', [])):
                    script_sig = vin.get('scriptsig', '')
                    witness = vin.get('witness', [])
                    prev_addr = vin.get('prevout', {}).get('scriptpubkey_address', '')
                    
                    if prev_addr == ADDRESS_PUZZLE_60 or script_sig or witness:
                        print(f"  Input #{vin_idx}: Originado de {prev_addr}")
                        if script_sig:
                            print(f"    scriptSig HEX: {script_sig}")
                        if witness:
                            print(f"    scriptWitness: {witness}")
                            
            return data
    except Exception as e:
        print(f"[-] Erro ao conectar na API Mempool: {e}")
        return []


if __name__ == "__main__":
    buscar_transacoes_puzzle()
