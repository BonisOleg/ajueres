"""Сервіси заявок: валідація, антиспам, збереження."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from .models import ContactInquiry

_RATE_LIMIT = 5
_RATE_WINDOW_SECONDS = 60 * 60
_EMAIL_RE = re.compile(
    r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$',
)
_PHONE_DIGITS_RE = re.compile(r'^\d{12}$')


class RateLimitExceeded(Exception):
    """Перевищено ліміт заявок з одного IP."""


@dataclass(frozen=True)
class ContactInquiryResult:
    inquiry: ContactInquiry | None
    skipped_honeypot: bool = False


def submit_contact_inquiry(
    *,
    purpose: str,
    name: str,
    phone: str,
    email: str,
    honeypot: str = '',
    ip_address: str | None = None,
    language: str | None = None,
) -> ContactInquiryResult:
    """
    Валідує й зберігає заявку.
    Honeypot заповнений → silent success без запису в БД.
    Rate limit: ≤5 / IP / годину.
    """
    if (honeypot or '').strip():
        return ContactInquiryResult(inquiry=None, skipped_honeypot=True)

    cleaned = _validate_fields(
        purpose=purpose,
        name=name,
        phone=phone,
        email=email,
    )

    if ip_address:
        _check_and_bump_rate_limit(ip_address)

    lang = _resolve_language(language)

    inquiry = ContactInquiry.objects.create(
        purpose=cleaned['purpose'],
        name=cleaned['name'],
        phone=cleaned['phone'],
        email=cleaned['email'],
        language=lang,
        status=ContactInquiry.Status.NEW,
        ip_address=ip_address or None,
    )

    return ContactInquiryResult(inquiry=inquiry, skipped_honeypot=False)


def _validate_fields(**raw: Any) -> dict[str, str]:
    errors: dict[str, list[str]] = {}

    purpose = (raw.get('purpose') or '').strip()
    if len(purpose) < 5:
        errors.setdefault('purpose', []).append(
            _('Укажите цель обращения (минимум 5 символов).')
        )
    elif len(purpose) > 2000:
        errors.setdefault('purpose', []).append(
            _('Максимум 2000 символов.')
        )

    name = _NAME_STRIP_RE.sub('', (raw.get('name') or '').strip())
    if not _is_valid_name(name):
        errors.setdefault('name', []).append(
            _('Имя должно содержать только буквы и быть не короче 2 символов.')
        )
    elif len(name) > 255:
        errors.setdefault('name', []).append(_('Максимум 255 символов.'))

    phone_raw = (raw.get('phone') or '').strip()
    phone = _normalize_uz_phone(phone_raw)
    if phone is None:
        errors.setdefault('phone', []).append(
            _('Введите корректный номер телефона в формате +998 (XX) XXX-XX-XX.')
        )

    email = (raw.get('email') or '').strip().lower()
    if not email or not _EMAIL_RE.match(email):
        errors.setdefault('email', []).append(
            _('Введите корректный адрес электронной почты.')
        )

    if errors:
        raise ValidationError(errors)

    return {
        'purpose': purpose,
        'name': name,
        'phone': phone or '',
        'email': email,
    }


_NAME_STRIP_RE = re.compile(r'[\u200b-\u200d\ufeff]')
_NAME_EXTRA = set(" -'’ʼ`")


def _is_valid_name(name: str) -> bool:
    name = _NAME_STRIP_RE.sub('', (name or '').strip())
    if len(name) < 2:
        return False
    has_letter = False
    for ch in name:
        if ch in _NAME_EXTRA:
            continue
        if ch.isdigit() or not ch.isalpha():
            return False
        has_letter = True
    return has_letter


def _normalize_uz_phone(value: str) -> str | None:
    """Повертає +998 (XX) XXX-XX-XX або None, якщо не 12 цифр з кодом 998."""
    digits = re.sub(r'\D', '', value or '')
    if not digits.startswith('998'):
        return None
    if not _PHONE_DIGITS_RE.match(digits):
        return None
    local = digits[3:]
    return f'+998 ({local[:2]}) {local[2:5]}-{local[5:7]}-{local[7:9]}'


def _resolve_language(language: str | None) -> str:
    allowed = {c.value for c in ContactInquiry.Language}
    lang = (language or get_language() or ContactInquiry.Language.RU)[:8]
    if lang not in allowed:
        return ContactInquiry.Language.RU
    return lang


def _rate_limit_key(ip_address: str) -> str:
    return f'contact_rate:{ip_address}'


def _check_and_bump_rate_limit(ip_address: str) -> None:
    """Фіксоване вікно: cache.add задає TTL; далі incr без скидання таймера."""
    key = _rate_limit_key(ip_address)
    if cache.add(key, 1, timeout=_RATE_WINDOW_SECONDS):
        return
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=_RATE_WINDOW_SECONDS)
        return
    if count > _RATE_LIMIT:
        raise RateLimitExceeded('Забагато заявок. Спробуйте пізніше.')
