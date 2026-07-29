"""Сервіси заявок: валідація, антиспам, збереження."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.translation import get_language

from .models import ContactInquiry

_PHONE_RE = re.compile(r'^[\d\s\+\-\(\)]+$')
_RATE_LIMIT = 5
_RATE_WINDOW_SECONDS = 60 * 60


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
        _enforce_rate_limit(ip_address)

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

    if ip_address:
        _bump_rate_limit(ip_address)

    return ContactInquiryResult(inquiry=inquiry, skipped_honeypot=False)


def _validate_fields(**raw: Any) -> dict[str, str]:
    errors: dict[str, list[str]] = {}

    purpose = (raw.get('purpose') or '').strip()
    if len(purpose) < 3:
        errors.setdefault('purpose', []).append('Мінімум 3 символи.')
    elif len(purpose) > 2000:
        errors.setdefault('purpose', []).append('Максимум 2000 символів.')

    name = (raw.get('name') or '').strip()
    if len(name) < 2:
        errors.setdefault('name', []).append('Мінімум 2 символи.')
    elif len(name) > 255:
        errors.setdefault('name', []).append('Максимум 255 символів.')

    phone = (raw.get('phone') or '').strip()
    if len(phone) < 5 or len(phone) > 64:
        errors.setdefault('phone', []).append('Довжина телефону 5–64 символи.')
    elif not _PHONE_RE.match(phone):
        errors.setdefault('phone', []).append('Недопустимі символи в телефоні.')

    email = (raw.get('email') or '').strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        errors.setdefault('email', []).append('Некоректний email.')

    if errors:
        raise ValidationError(errors)

    return {
        'purpose': purpose,
        'name': name,
        'phone': phone,
        'email': email,
    }


def _resolve_language(language: str | None) -> str:
    allowed = {c.value for c in ContactInquiry.Language}
    lang = (language or get_language() or ContactInquiry.Language.RU)[:8]
    if lang not in allowed:
        return ContactInquiry.Language.RU
    return lang


def _rate_limit_key(ip_address: str) -> str:
    return f'contact_rate:{ip_address}'


def _enforce_rate_limit(ip_address: str) -> None:
    data = cache.get(_rate_limit_key(ip_address)) or {'count': 0, 'started': None}
    count = int(data.get('count') or 0)
    if count >= _RATE_LIMIT:
        raise RateLimitExceeded('Забагато заявок. Спробуйте пізніше.')


def _bump_rate_limit(ip_address: str) -> None:
    key = _rate_limit_key(ip_address)
    data = cache.get(key) or {'count': 0, 'started': timezone.now().isoformat()}
    count = int(data.get('count') or 0) + 1
    cache.set(
        key,
        {'count': count, 'started': data.get('started')},
        timeout=_RATE_WINDOW_SECONDS,
    )
