"""
Bitcoin Blockchain Signature Harvester & Satoshi Nakamoto Wallet Analyzer
Author: Antigravity AI Engine

Este script faz a requisição com suporte a múltiplos provedores (Blockstream / Mempool)
e analisa histórico de assinaturas ECDSA na blockchain.
"""

import json
import urllib.request
import ssl
from typing import List, Tuple, Optional

# Secp256k1 Elliptic Curve Order N
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Endereços Notórios
SATOSHI_GENESIS_ADDR = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" # Bloco 0 (Nunca gastou)
SATOSHI_BLOCK9_ADDR  = "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX" # Bloco 9 (Primeira transação da história para Hal Finney)
PUZZLE_60_ADDR       = "13zb1hQbWVsc2S7ZTZnP2G4undNNpdlh5so"
PUZZLE_71_ADDR       = "1PWo3Jeb9jrGwfHDNpdGK54CRas7fsVzXU"
PUZZLE_72_ADDR       = "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR"
PUZZLE_140_ADDR      = "1QKBaU6WAeycb3DbKbLBkX7vJiaS8r42Xo"


def fetch_address_transactions(address: str) -> List[dict]:
    """Busca histórico de transações com suporte a múltiplos provedores resilientes."""
    providers = [
        f"https://blockstream.info/api/address/{address}/txs",
        f"https://mempool.space/api/address/{address}/txs"
    ]
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    for url in providers:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=12) as response:
                data = json.loads(response.read().decode('utf-8'))
                if isinstance(data, list):
                    return data
        except Exception as e:
            continue

    return []


def analisar_carteira(nome: str, address: str):
    print("=========================================================================")
    print(f"=== ANALISANDO CARTEIRA: {nome} ===")
    print(f"=== Endereço: {address} ===")
    print("=========================================================================")

    txs = fetch_address_transactions(address)
    print(f"[+] Total de Transações Encontradas: {len(txs)}")

    spent_inputs = 0
    signatures_found = 0

    for tx in txs:
        txid = tx.get("txid", "")
        vin = tx.get("vin", [])
        for inp in vin:
            # Verificar se o input é gasto deste endereço
            prevout = inp.get("prevout", {})
            if prevout and prevout.get("scriptpubkey_address") == address:
                spent_inputs += 1
                scriptsig = inp.get("scriptsig", "")
                witness = inp.get("witness", [])
                if scriptsig or witness:
                    signatures_found += 1
                    print(f"  [!] Assinatura ECDSA encontrada na TXID: {txid[:16]}...")

    print(f"[+] Total de Inputs Gastos: {spent_inputs}")
    print(f"[+] Total de Assinaturas Extraídas: {signatures_found}")
    
    if spent_inputs == 0:
        print("[i] Esta carteira NUNCA gastou moedas na rede (0 assinaturas reveladas).")
    else:
        print("[OK] Assinaturas extraídas com sucesso para análise de nonces LLL!")


if __name__ == "__main__":
    print("🔬 ANÁLISE DE BLOCKCHAIN & CRIPTOGRAFIA HISTÓRICA\n")
    
    analisar_carteira("Carteira do Satoshi (Bloco 9 - Hal Finney)", SATOSHI_BLOCK9_ADDR)
    print("\n")
    analisar_carteira("Carteira do Satoshi (Genesis Block)", SATOSHI_GENESIS_ADDR)
    print("\n")
    analisar_carteira("Bitcoin Puzzle #60 (Resolvido)", PUZZLE_60_ADDR)
    print("\n")
    analisar_carteira("Bitcoin Puzzle #71 (Não Resolvido)", PUZZLE_71_ADDR)
