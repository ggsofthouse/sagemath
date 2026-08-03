"""
Análise do Endereço Pai Criador do Challenge (1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F)
Extrai todas as assinaturas ECDSA do criador dos Puzzles no Bloco 339085.
"""

import json
import urllib.request

PARENT_ADDRESS = "1Czoy8xtddvcGrEhUUCZDQ9QqdRfKh697F"


def parse_der_sig(sig_hex: str):
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
        return r, s
    except Exception as e:
        return None


def analise_parent():
    print("=========================================================================")
    print("   ANALISANDO O ENDEREÇO PAI DO CRIADOR DO PUZZLE (1Czoy8...)")
    print("=========================================================================")

    url = f"https://mempool.space/api/address/{PARENT_ADDRESS}/txs"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        txs = json.loads(resp.read().decode('utf-8'))

    print(f"[+] Total de Transações do Criador dos Puzzles: {len(txs)}")

    sigs = []
    for idx, tx in enumerate(txs):
        txid = tx['txid']
        for vin in tx.get('vin', []):
            script_sig = vin.get('scriptsig', '')
            if script_sig:
                sig_len = int(script_sig[:2], 16)
                sig_hex = script_sig[2 : 2 + sig_len * 2]
                parsed = parse_der_sig(sig_hex)
                if parsed:
                    r, s = parsed
                    sigs.append((txid, r, s))
                    print(f"  TXID: {txid[:16]}... | r = {hex(r)[:18]}... | s = {hex(s)[:18]}...")

    print(f"[+] Total de Assinaturas do Criador Coletadas: {len(sigs)}")

if __name__ == "__main__":
    analise_parent()
