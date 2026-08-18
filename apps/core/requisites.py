"""Parse and normalize public-offer requisites rows (label + value)."""

from __future__ import annotations

import json
from typing import Any

REQUISITES_RU = (
    ('ИНН', ''),
    ('р/с', ''),
    ('Банк', ''),
    ('Адрес', ''),
)
REQUISITES_UZ = (
    ('STIR', ''),
    ('Hisob raqami', ''),
    ('Bank', ''),
    ('Manzil', ''),
)
REQUISITES_EN = (
    ('TIN', ''),
    ('Account', ''),
    ('Bank', ''),
    ('Address', ''),
)

_STANDARD_ALIASES = (
    frozenset({'инн', 'stir', 'tin'}),
    frozenset({'р/с', 'р/c', 'рс', 'hisob raqami', 'account'}),
    frozenset({'банк', 'bank'}),
    frozenset({'адрес', 'manzil', 'address'}),
)


def rows_from_pairs(pairs: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
    return [{'label': label, 'value': value} for label, value in pairs]


def lang_from_field_name(name: str) -> str:
    if name.endswith('_uz'):
        return 'uz'
    if name.endswith('_en'):
        return 'en'
    return 'ru'


def default_rows_for_lang(lang: str) -> list[dict[str, str]]:
    code = (lang or 'ru')[:2]
    if code == 'uz':
        return rows_from_pairs(REQUISITES_UZ)
    if code == 'en':
        return rows_from_pairs(REQUISITES_EN)
    return rows_from_pairs(REQUISITES_RU)


def parse_requisites_text(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in (text or '').splitlines():
        raw = line.strip()
        if not raw:
            continue
        if ':' in raw:
            label, value = raw.split(':', 1)
            rows.append({'label': label.strip(), 'value': value.strip()})
        else:
            rows.append({'label': '', 'value': raw})
    return rows


def normalize_requisites(value: Any) -> list[dict[str, str]]:
    if value is None or value == '':
        return []
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith('['):
            try:
                loaded = json.loads(text)
            except json.JSONDecodeError:
                return parse_requisites_text(text)
            if not isinstance(loaded, list):
                return parse_requisites_text(text)
            items = loaded
        else:
            return parse_requisites_text(text)
    else:
        return []

    rows: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        label = str(item.get('label') or '').strip()
        val = str(item.get('value') or '').strip()
        if not label and not val:
            continue
        rows.append({'label': label, 'value': val})
    return rows


def _alias_index(label: str) -> int | None:
    folded = label.casefold()
    for index, aliases in enumerate(_STANDARD_ALIASES):
        if folded in aliases:
            return index
    return None


def display_requisites_rows(value: Any, lang: str = 'ru') -> list[dict[str, str]]:
    """Always include INN/account/bank/address, plus any extra custom rows."""
    saved = normalize_requisites(value)
    standard = default_rows_for_lang(lang)
    matched: set[int] = set()
    for row in saved:
        index = _alias_index(row['label'])
        if index is None or index in matched:
            continue
        standard[index] = {
            'label': standard[index]['label'],
            'value': row['value'],
        }
        matched.add(index)
    extra = [row for row in saved if _alias_index(row['label']) is None]
    return [*standard, *extra]


def visible_requisites_rows(value: Any, lang: str = 'ru') -> list[dict[str, str]]:
    return display_requisites_rows(value, lang)
