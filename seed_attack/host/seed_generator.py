"""
GERADOR DE CANDIDATOS DE SEMENTE - HOST CPU
Autor: Antigravity AI Engine
"""

import math
import random
from datetime import datetime

class SeedGenerator:
    @staticmethod
    def generate_timestamps(year_start=2014, year_end=2015, count=100000000):
        """Gera sementes baseadas no Timestamp UNIX dos anos de criação dos Puzzles (2014-2015)."""
        start_ts = int(datetime(year_start, 1, 1).timestamp())
        end_ts   = int(datetime(year_end, 12, 31, 23, 59, 59).timestamp())
        for ts in range(start_ts, min(start_ts + count, end_ts)):
            yield ts

    @staticmethod
    def generate_weak_32bit(start=0, count=100000000):
        """Gera sementes inteiras de 32-bits."""
        for num in range(start, start + count):
            yield num

    @staticmethod
    def generate_wordlist_passphrases(words, max_pass_len=4):
        """Gera combinações de palavras da semente + passphrases."""
        for word in words:
            yield word
            for i in range(100):
                yield f"{word}{i}"
                yield f"{word}_{i}"
