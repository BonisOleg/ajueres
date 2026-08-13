"""Theme / style models: global button fills + per-section overrides."""

from __future__ import annotations

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .theme_fields import (
    BUTTON_ROLES,
    BUTTON_STYLE_DEFAULTS,
    DEFAULT_GRADIENT_ANGLE,
    DEFAULT_GRADIENT_END,
    DEFAULT_GRADIENT_START,
    FILL_GRADIENT,
    FillStyleMixin,
    SECTION_STYLE_KEYS,
    validate_hex_color,
)


_CACHE_BUTTONS = 'site_button_styles'
_CACHE_BLOCK_STYLES = 'block_styles_all'


class SiteButtonStyle(FillStyleMixin):
    """Глобальні стилі кнопок (primary / secondary / header / modal)."""

    role = models.CharField(
        _('Роль кнопки'),
        max_length=32,
        choices=BUTTON_ROLES,
        unique=True,
    )

    class Meta:
        verbose_name = 'Стиль кнопки'
        verbose_name_plural = 'Стили кнопок'
        ordering = ['role']

    def __str__(self):
        return self.get_role_display()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        cache.delete(_CACHE_BUTTONS)
        cache.delete('site_settings')

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete(_CACHE_BUTTONS)
        return result

    def apply_site_default(self) -> None:
        payload = BUTTON_STYLE_DEFAULTS.get(self.role)
        if not payload:
            return
        for field, value in payload.items():
            setattr(self, field, value)

    def is_site_default(self) -> bool:
        payload = BUTTON_STYLE_DEFAULTS.get(self.role)
        if not payload:
            return False
        return all(getattr(self, field) == value for field, value in payload.items())

    @classmethod
    def ensure_defaults(cls) -> list['SiteButtonStyle']:
        result = []
        for role, payload in BUTTON_STYLE_DEFAULTS.items():
            obj, _ = cls.objects.get_or_create(role=role, defaults=payload)
            result.append(obj)
        return result


class BlockStyle(FillStyleMixin):
    """Стилі секції: фон + опційний override заливки кнопок секції."""

    page = models.CharField(_('Страница'), max_length=64, db_index=True)
    section_key = models.CharField(_('Секция'), max_length=64)
    label = models.CharField(_('Название в админке'), max_length=128, blank=True)
    bg_color = models.CharField(
        _('Цвет фона секции'),
        max_length=7,
        blank=True,
        default='',
        help_text=_('Hex. Пусто = CSS по умолчанию'),
    )
    bg_image = models.ImageField(
        _('Фоновое изображение'),
        upload_to='cms/section-bg/',
        blank=True,
        null=True,
        help_text=_('Если задано — покрывает секцию. Цвет остаётся запасным фоном.'),
    )
    override_button_fill = models.BooleanField(
        _('Override заливки кнопок в секции'),
        default=False,
        help_text=_('Если включено — fill_* ниже заменяют глобальные стили кнопок в этой секции'),
    )

    class Meta:
        verbose_name = 'Стиль секции'
        verbose_name_plural = 'Стили секций'
        ordering = ['page', 'section_key']
        constraints = [
            models.UniqueConstraint(
                fields=['page', 'section_key'],
                name='uniq_blockstyle_page_section',
            ),
        ]

    def __str__(self):
        return self.label or f'{self.page}.{self.section_key}'

    def clean(self):
        try:
            validate_hex_color(self.bg_color, allow_blank=True)
        except ValidationError as exc:
            raise ValidationError({'bg_color': exc}) from exc

        if self.override_button_fill:
            super().clean()
        else:
            # Skip strict fill validation when override off
            models.Model.clean(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.label:
            for page, key, title in SECTION_STYLE_KEYS:
                if page == self.page and key == self.section_key:
                    self.label = title
                    break
        super().save(*args, **kwargs)
        cache.delete(_CACHE_BLOCK_STYLES)

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete(_CACHE_BLOCK_STYLES)
        return result

    @property
    def cache_key(self) -> str:
        return f'{self.page}.{self.section_key}'

    def section_inline_style(self) -> str:
        parts: list[str] = []
        bg = (self.bg_color or '').strip()
        if bg:
            parts.append(f'background-color: {bg};')
        image = self.bg_image
        if image:
            try:
                url = image.url
            except ValueError:
                url = ''
            if url:
                parts.append(f'background-image: url("{url}");')
                parts.append('background-size: cover;')
                parts.append('background-position: center;')
                parts.append('background-repeat: no-repeat;')
        return ' '.join(parts)

    @classmethod
    def ensure_defaults(cls) -> int:
        created = 0
        for page, key, title in SECTION_STYLE_KEYS:
            _, was_created = cls.objects.get_or_create(
                page=page,
                section_key=key,
                defaults={
                    'label': title,
                    'fill_type': FILL_GRADIENT,
                    'gradient_start': DEFAULT_GRADIENT_START,
                    'gradient_end': DEFAULT_GRADIENT_END,
                    'gradient_angle': DEFAULT_GRADIENT_ANGLE,
                    'override_button_fill': False,
                },
            )
            if was_created:
                created += 1
        return created
