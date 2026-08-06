"""
GERADOR DE CANDIDATOS DE SEMENTE ULTRA-BRUTO - HOST CPU
Autor: Antigravity AI Engine

Geração Massiva de Hipóteses:
  1. Timestamps UNIX Estendidos (2013-2017) em formato int e byte
  2. Multi-Hashes (SHA256(int), SHA256(str), SHA1, MD5)
  3. Sementes numéricas de 32, 40, 48, 56 e 64 bits
  4. Passphrases / Brainwallets de dicionários cripto expandidos com separadores ("", "_", "-", " ") e sufixos 0-1000
"""

import math
import hashlib
import random
from datetime import datetime

class SeedGenerator:
    @staticmethod
    def generate_timestamps(year_start=2013, year_end=2017, count=10**12):
        """Gera sementes de Timestamps UNIX dos anos de criação do puzzle (2013-2017)."""
        start_ts = int(datetime(year_start, 1, 1).timestamp())
        end_ts   = int(datetime(year_end, 12, 31, 23, 59, 59).timestamp())
        for ts in range(start_ts, end_ts + 1):
            yield ts

    @staticmethod
    def generate_sha256_timestamps(year_start=2013, year_end=2017, count=10**12):
        """Gera Hashes SHA256 e variantes de timestamps inteiros e strings."""
        start_ts = int(datetime(year_start, 1, 1).timestamp())
        end_ts   = int(datetime(year_end, 12, 31, 23, 59, 59).timestamp())
        for ts in range(start_ts, end_ts + 1):
            ts_bytes = ts.to_bytes(8, 'big')
            ts_str_bytes = str(ts).encode('utf-8')

            yield hashlib.sha256(ts_bytes).digest()
            yield hashlib.sha256(ts_str_bytes).digest()

    @staticmethod
    def generate_multi_hashes(year_start=2013, year_end=2017, count=10**12):
        """Gera Hashes SHA256, SHA1 e MD5 de timestamps inteiros e strings."""
        start_ts = int(datetime(year_start, 1, 1).timestamp())
        end_ts   = int(datetime(year_end, 12, 31, 23, 59, 59).timestamp())
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
        """Gera sementes numéricas de 32 a 48 bits."""
        for num in range(0, 1 << end_bit):
            yield num

    @staticmethod
    def generate_wordlist_passphrases(words=None, max_pass_len=4):
        """Gera passphrases de palavras-chave clássicas de Bitcoin com dicionário expandido e separadores."""
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
