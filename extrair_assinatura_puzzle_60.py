"""
Extração Precisa da Assinatura ECDSA do Bitcoin Puzzle #60
Endereço Alvo: 1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su
PublicKey Alvo: 0348e843dc5b1bd246e6309b4924b81543d02b16c8083df973a89ce2c7eb89a10d
Range Alvo: [0x800000000000000 ... 0xfffffffffffffff] (2^59 .. 2^60-1)
"""

import json
import urllib.request
import binascii

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
ADDRESS_PUZZLE_60 = "1Kn5h2qpgw9mWE5jKpk8PP4qvvJ1QVy8su"
PUBKEY_PUZZLE_60 = "0348e843dc5b1bd246e6309b4924b81543d02b16c8083df973a89ce2c7eb89a10d"


def parse_der_signature(sig_hex: str):
    """
    Decodifica uma assinatura DER ECDSA padrão de transação Bitcoin
    Retorna (r, s, hashtype) em formato inteiro.
    Format DER: 30 <len_total> 02 <len_r> <r> 02 <len_s> <s> <hashtype>
    """
    try:
        raw = bytes.fromhex(sig_hex)
        if raw[0] != 0x30:
            return None
        
        idx = 2
        if raw[idx] != 0x02:
            return None
        len_r = raw[idx + 1]
        r_bytes = raw[idx + 2 : idx + 2 + len_r]
        r = int.from_bytes(r_bytes, byteorder='big')
        
        idx = idx + 2 + len_r
        if raw[idx] != 0x02:
            return None
        len_s = raw[idx + 1]
        s_bytes = raw[idx + 2 : idx + 2 + len_s]
        s = int.from_bytes(s_bytes, byteorder='big')
        
        hashtype = raw[-1]
        return r, s, hashtype
    except Exception as e:
        return None


def analise_detalhada_puzzle_60():
    print("=========================================================================")
    print("   ANÁLISE PASSO A PASSO DO PUZZLE #60 (BLOCKCHAIN REAL)")
    print(f"   Endereço: {ADDRESS_PUZZLE_60}")
    print(f"   PublicKey: {PUBKEY_PUZZLE_60}")
    print("=========================================================================")

    url = f"https://mempool.space/api/address/{ADDRESS_PUZZLE_60}/txs"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        txs = json.loads(resp.read().decode('utf-8'))

    spending_tx = None
    sig_r = sig_s = None

    for tx in txs:
        txid = tx['txid']
        for vin in tx.get('vin', []):
            prev_addr = vin.get('prevout', {}).get('scriptpubkey_address', '')
            if prev_addr == ADDRESS_PUZZLE_60:
                print(f"[!] ENCONTRADA A TRANSAÇÃO DE RESGATE (SPENDING TX) DO PUZZLE #60!")
                print(f"    TXID: {txid}")
                
                script_sig = vin.get('scriptsig', '')
                witness = vin.get('witness', [])
                
                print(f"    scriptSig Hex: {script_sig}")
                
                # DER Signature costuma ser a primeira parte do scriptSig
                # scriptSig em P2PKH: <len_sig> <sig_der> <len_pubkey> <pubkey>
                if script_sig:
                    sig_len = int(script_sig[:2], 16)
                    sig_hex = script_sig[2 : 2 + sig_len * 2]
                    pubkey_hex = script_sig[2 + sig_len * 2 + 2 :]
                    
                    parsed = parse_der_signature(sig_hex)
                    if parsed:
                        sig_r, sig_s, hashtype = parsed
                        print(f"\n[+] Assinatura DER ECDSA Extraída da Blockchain:")
                        print(f"    r (Hex): {hex(sig_r)}")
                        print(f"    s (Hex): {hex(sig_s)}")
                        print(f"    HashType: {hashtype}")
                        print(f"    PubKey na Transação: {pubkey_hex}")

    return sig_r, sig_s

if __name__ == "__main__":
    analise_detalhada_puzzle_60()
