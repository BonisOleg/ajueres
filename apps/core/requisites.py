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


def rows_from_pairs(pairs: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
    return [{'label': label, 'value': value} for label, value in pairs]


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


def visible_requisites_rows(value: Any) -> list[dict[str, str]]:
    return normalize_requisites(value)
