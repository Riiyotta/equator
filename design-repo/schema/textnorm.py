"""Text normalisation shared by extraction/build_leakage_patterns.py and schema/semantic_validate.py (one implementation).

normalize(): NFKC; zero-width / soft-hyphen characters removed; common Cyrillic/Greek look-alikes folded to Latin;
curly quotes -> straight; every dash variant -> '-'; diacritics stripped (Goncalves == Gonçalves); lower-case;
whitespace collapsed. shingles(): hashed-ready 5-word windows of the punctuation-stripped normalised text.
"""
import re
import unicodedata

ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿­᠎"), None)
FOLD = str.maketrans({
    "а": "a", "е": "e", "і": "i", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
    "к": "k", "м": "m", "т": "t", "в": "b", "н": "h",
    "А": "a", "Е": "e", "І": "i", "О": "o", "Р": "p", "С": "c", "У": "y", "Х": "x",
    "К": "k", "М": "m", "Т": "t", "В": "b", "Н": "h",
    "ο": "o", "ι": "i", "ε": "e", "α": "a", "ρ": "p", "υ": "u", "κ": "k", "ν": "v",
    "Ι": "i", "Ο": "o", "Ε": "e", "Α": "a", "Ρ": "p", "Υ": "y", "Κ": "k",
    "‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'", "“": '"', "”": '"', "„": '"', "″": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "―": "-", "−": "-", "﹘": "-", "﹣": "-", "－": "-",
    "º": "o", "ª": "a",
})


def normalize(s):
    s = unicodedata.normalize("NFKC", s).translate(ZERO_WIDTH).translate(FOLD)
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower()).strip()


def words_only(s):
    return re.sub(r"[^a-z0-9$%' ]+", " ", normalize(s)).replace("'", "").split()


def shingles(s, n=5):
    w = words_only(s)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
