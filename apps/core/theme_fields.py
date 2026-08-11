"""DRY helpers for solid/gradient fill fields and CSS generation."""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

HEX_COLOR_RE = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')

FILL_SOLID = 'solid'
FILL_GRADIENT = 'gradient'
FILL_TYPE_CHOICES = (
    (FILL_SOLID, _('Однотонний')),
    (FILL_GRADIENT, _('Градієнт')),
)

DEFAULT_ACCENT = '#ff5a36'
DEFAULT_ACCENT_INK = '#db3f1c'
DEFAULT_ACCENT_SOFT = '#fff0ea'
DEFAULT_GRADIENT_START = '#ff7a52'
DEFAULT_GRADIENT_END = '#e04822'
DEFAULT_GRADIENT_ANGLE = 145

BUTTON_ROLES = (
    ('primary', _('Primary (основна CTA)')),
    ('secondary', _('Secondary')),
    ('header', _('Header')),
    ('modal', _('Modal')),
)

SECTION_STYLE_KEYS = (
    ('home', 'hero', 'Головна — Hero'),
    ('home', 'advantages', 'Головна — Переваги'),
    ('home', 'brands', 'Головна — Бренди'),
    ('home', 'stats', 'Головна — Статистика'),
    ('home', 'coop', 'Головна — Співпраця'),
    ('home', 'cases', 'Головна — Кейси'),
    ('home', 'cta', 'Головна — CTA'),
    ('about', 'intro', 'Про компанію — Intro'),
    ('about', 'content', 'Про компанію — Контент'),
    ('about', 'cta', 'Про компанію — CTA'),
    ('products', 'catalog', 'Каталог'),
    ('products', 'brands', 'Каталог — Бренди'),
    ('contacts', 'intro', 'Контакти — Intro'),
    ('contacts', 'form', 'Контакти — Форма'),
    ('contacts', 'partners', 'Контакти — Партнери'),
    ('contacts', 'map', 'Контакти — Карта'),
    ('site', 'header', 'Сайт — Header'),
    ('site', 'footer', 'Сайт — Footer'),
    ('site', 'modal', 'Сайт — Modal'),
)


def validate_hex_color(value: str, *, allow_blank: bool = True) -> None:
    raw = (value or '').strip()
    if not raw:
        if allow_blank:
            return
        raise ValidationError(_('Колір обовʼязковий (Hex, напр. #FF5A36).'))
    if not HEX_COLOR_RE.match(raw):
        raise ValidationError(_('Невірний Hex-колір. Приклад: #FF5A36'))


def normalize_hex(value: str, default: str = '') -> str:
    raw = (value or '').strip()
    if not raw:
        return default
    if len(raw) == 4 and raw.startswith('#'):
        return '#' + ''.join(ch * 2 for ch in raw[1:]).lower()
    return raw.lower()


def fill_css_background(
    *,
    fill_type: str,
    solid_color: str = '',
    gradient_start: str = '',
    gradient_end: str = '',
    gradient_angle: int | None = None,
    fallback: str = '',
) -> str:
    """CSS background value for a fill config."""
    if fill_type == FILL_GRADIENT:
        start = normalize_hex(gradient_start) or DEFAULT_GRADIENT_START
        end = normalize_hex(gradient_end) or DEFAULT_GRADIENT_END
        angle = gradient_angle if gradient_angle is not None else DEFAULT_GRADIENT_ANGLE
        return f'linear-gradient({int(angle)}deg, {start} 0%, {end} 100%)'
    solid = normalize_hex(solid_color)
    if solid:
        return solid
    return fallback


def validate_fill_payload(
    *,
    fill_type: str,
    solid_color: str = '',
    gradient_start: str = '',
    gradient_end: str = '',
    gradient_angle: int | None = None,
    require_complete: bool = False,
    field_prefix: str = '',
) -> dict[str, ValidationError]:
    """Return {field_name: ValidationError} for conflicting fill data."""
    errors: dict[str, ValidationError] = {}
    p = f'{field_prefix}_' if field_prefix else ''

    try:
        validate_hex_color(solid_color, allow_blank=True)
    except ValidationError as exc:
        errors[f'{p}solid_color'] = exc

    try:
        validate_hex_color(gradient_start, allow_blank=True)
    except ValidationError as exc:
        errors[f'{p}gradient_start'] = exc

    try:
        validate_hex_color(gradient_end, allow_blank=True)
    except ValidationError as exc:
        errors[f'{p}gradient_end'] = exc

    if fill_type == FILL_GRADIENT:
        if require_complete or (gradient_start or gradient_end or gradient_angle is not None):
            if not (gradient_start or '').strip():
                errors[f'{p}gradient_start'] = ValidationError(
                    _('Для градієнта вкажіть початковий колір.')
                )
            if not (gradient_end or '').strip():
                errors[f'{p}gradient_end'] = ValidationError(
                    _('Для градієнта вкажіть кінцевий колір.')
                )
        if gradient_angle is not None and not (0 <= int(gradient_angle) <= 360):
            errors[f'{p}gradient_angle'] = ValidationError(
                _('Кут градієнта має бути в діапазоні 0–360.')
            )
    elif fill_type == FILL_SOLID and require_complete and not (solid_color or '').strip():
        errors[f'{p}solid_color'] = ValidationError(
            _('Для однотонної заливки вкажіть колір.')
        )

    return errors


class FillStyleMixin(models.Model):
    """Abstract solid/gradient fill fields with model-level validation."""

    fill_type = models.CharField(
        _('Тип заливки'),
        max_length=16,
        choices=FILL_TYPE_CHOICES,
        default=FILL_GRADIENT,
    )
    solid_color = models.CharField(
        _('Однотонний колір'),
        max_length=7,
        blank=True,
        default='',
        help_text=_('Hex, напр. #FF5A36'),
    )
    gradient_start = models.CharField(
        _('Градієнт — початок'),
        max_length=7,
        blank=True,
        default=DEFAULT_GRADIENT_START,
        help_text=_('Hex'),
    )
    gradient_end = models.CharField(
        _('Градієнт — кінець'),
        max_length=7,
        blank=True,
        default=DEFAULT_GRADIENT_END,
        help_text=_('Hex'),
    )
    gradient_angle = models.PositiveSmallIntegerField(
        _('Кут градієнта (°)'),
        default=DEFAULT_GRADIENT_ANGLE,
        help_text=_('0–360'),
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        errors = validate_fill_payload(
            fill_type=self.fill_type,
            solid_color=self.solid_color,
            gradient_start=self.gradient_start,
            gradient_end=self.gradient_end,
            gradient_angle=self.gradient_angle,
            require_complete=True,
        )
        if errors:
            raise ValidationError(errors)

    def as_css_background(self, fallback: str = '') -> str:
        return fill_css_background(
            fill_type=self.fill_type,
            solid_color=self.solid_color,
            gradient_start=self.gradient_start,
            gradient_end=self.gradient_end,
            gradient_angle=self.gradient_angle,
            fallback=fallback,
        )

    def has_custom_fill(self) -> bool:
        if self.fill_type == FILL_SOLID:
            return bool((self.solid_color or '').strip())
        return bool((self.gradient_start or '').strip() and (self.gradient_end or '').strip())
