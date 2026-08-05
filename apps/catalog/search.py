"""
Нормалізація тексту для пошуку в каталозі.

Пошук не покладається на SQL-регістронезалежність: SQLite ILIKE ігнорує
регістр лише для ASCII, тому кирилиця складається в нижній регістр у Python,
а в БД зберігається вже нормалізований `Product.search_text`.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

SEARCH_MIN_LEN = 2
SEARCH_MAX_LEN = 100
MAX_TOKENS = 8

_NON_WORD_RE = re.compile(r'[\W_]+', re.UNICODE)


def normalize_text(value: str | None) -> str:
    """
    Приводить рядок до пошукової форми: NFKC, нижній регістр, ё→е,
    будь-яка пунктуація («», лапки, дефіси, крапки) → пробіл.

    '«Рисова бумага», 100 гр.' → 'рисова бумага 100 гр'
    """
    if not value:
        return ''
    text = unicodedata.normalize('NFKC', str(value)).casefold()
    text = text.replace('ё', 'е')
    text = _NON_WORD_RE.sub(' ', text)
    return ' '.join(text.split())


def tokenize(value: str | None) -> list[str]:
    """Унікальні токени запиту в порядку введення, не більше MAX_TOKENS."""
    tokens: list[str] = []
    for token in normalize_text(value).split(' '):
        if token and token not in tokens:
            tokens.append(token)
        if len(tokens) >= MAX_TOKENS:
            break
    return tokens


def build_search_text(parts: Iterable[str | None]) -> str:
    """Склеює нормалізовані частини товару, відкидаючи дублі (ru/uz/en збіги)."""
    chunks: list[str] = []
    for part in parts:
        chunk = normalize_text(part)
        if chunk and chunk not in chunks:
            chunks.append(chunk)
    return ' '.join(chunks)
