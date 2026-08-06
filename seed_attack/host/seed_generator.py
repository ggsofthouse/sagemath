"""
GERADOR DE CANDIDATOS DE SEMENTE ULTRA-BRUTO - HOST CPU
Autor: Antigravity AI Engine

Foco Histórico Bitcointalk:
  Prioridade Máxima: Janeiro a Abril de 2015 (data real de lançamento dos Puzzles).
"""

import math
import hashlib
import random
from datetime import datetime

class SeedGenerator:
    @staticmethod
    def generate_timestamps(year_start=2015, year_end=2015):
        """Gera sementes de Timestamps UNIX priorizando a janela real do Bitcointalk (Jan 2015 - Mai 2015)."""
        # Janela Prioritária: Jan 2015 a Mai 2015
        start_priority = int(datetime(2015, 1, 1).timestamp())
        end_priority   = int(datetime(2015, 5, 31, 23, 59, 59).timestamp())
        for ts in range(start_priority, end_priority + 1):
            yield ts

        # Extensão Secundária: Restante de 2014 e 2015
        start_ts = int(datetime(2014, 1, 1).timestamp())
        end_ts   = int(datetime(2015, 12, 31, 23, 59, 59).timestamp())
        for ts in range(start_ts, end_ts + 1):
            if not (start_priority <= ts <= end_priority):
                yield ts

    @staticmethod
    def generate_sha256_timestamps(year_start=2015, year_end=2015):
        """Gera Hashes SHA256 e variantes de timestamps focados na janela Jan 2015 - Mai 2015."""
        start_priority = int(datetime(2015, 1, 1).timestamp())
        end_priority   = int(datetime(2015, 5, 31, 23, 59, 59).timestamp())
        
        for ts in range(start_priority, end_priority + 1):
            ts_bytes = ts.to_bytes(8, 'big')
            ts_str_bytes = str(ts).encode('utf-8')
            yield hashlib.sha256(ts_bytes).digest()
            yield hashlib.sha256(ts_str_bytes).digest()

        start_ts = int(datetime(2014, 1, 1).timestamp())
        end_ts   = int(datetime(2015, 12, 31, 23, 59, 59).timestamp())
        for ts in range(start_ts, end_ts + 1):
            if not (start_priority <= ts <= end_priority):
                ts_bytes = ts.to_bytes(8, 'big')
                ts_str_bytes = str(ts).encode('utf-8')
                yield hashlib.sha256(ts_bytes).digest()
                yield hashlib.sha256(ts_str_bytes).digest()

    @staticmethod
    def generate_multi_hashes(year_start=2015, year_end=2015):
        """Gera Multi-Hashes (SHA256, SHA1, MD5) focados na janela Jan-Mai 2015."""
        start_ts = int(datetime(2015, 1, 1).timestamp())
        end_ts   = int(datetime(2015, 5, 31, 23, 59, 59).timestamp())
        for ts in range(start_ts, end_ts + 1):
            ts_bytes = ts.to_bytes(8, 'big')
            ts_str_bytes = str(ts).encode('utf-8')
            yield hashlib.sha256(ts_bytes).digest()
            yield hashlib.sha256(ts_str_bytes).digest()
            yield hashlib.sha1(ts_bytes).digest()
            yield hashlib.md5(ts_str_bytes).digest()

    @staticmethod
    def generate_40_48bit(start=0, count=10**12):
        """Gera sementes numéricas de 40 a 48 bits."""
        end_range = min(start + count, 1 << 48)
        for num in range(start, end_range):
            yield num

    @staticmethod
    def generate_bits_range(start_bit=32, end_bit=48, step_count=100000000):
        for num in range(0, 1 << end_bit):
            yield num

    @staticmethod
    def generate_wordlist_passphrases(words=None, max_pass_len=4):
        """Gera passphrases de palavras-chave clássicas de Bitcoin com dicionário expandido."""
        if not words:
            words = [
                "bitcoin", "satoshi", "puzzle", "nakamoto", "genesis", "secret",
                "wallet", "key", "passphrase", "master", "seed", "blockchain",
                "crypto", "private", "public", "coin", "gold", "money", "vault",
                "password", "admin", "root", "test", "123456", "qwerty",
                "letmein", "welcome", "monkey", "dragon", "master", "login"
            ]
        for w in words:
            yield w.encode('utf-8')
            yield hashlib.sha256(w.encode('utf-8')).digest()
            for i in range(0, 1001):
                for sep in ["", "_", "-", " "]:
                    phrase = f"{w}{sep}{i}"
                    yield phrase.encode('utf-8')
                    yield hashlib.sha256(phrase.encode('utf-8')).digest()

    @staticmethod
    def generate_brainwallet_dictionary():
        return SeedGenerator.generate_wordlist_passphrases()
