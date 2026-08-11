"""Theme CSS helpers for templates (global + section overrides)."""

from __future__ import annotations

from django.utils.html import escape
from django.utils.safestring import mark_safe

from .theme_fields import (
    DEFAULT_ACCENT,
    DEFAULT_ACCENT_INK,
    DEFAULT_ACCENT_SOFT,
    fill_css_background,
)


def build_theme_root_css(settings_obj, button_styles: dict) -> str:
    accent = escape((getattr(settings_obj, 'accent_color', None) or DEFAULT_ACCENT).strip())
    accent_ink = escape(
        (getattr(settings_obj, 'accent_ink', None) or DEFAULT_ACCENT_INK).strip()
    )
    accent_soft = escape(
        (getattr(settings_obj, 'accent_soft', None) or DEFAULT_ACCENT_SOFT).strip()
    )

    lines = [
        f'--accent: {accent};',
        f'--accent-ink: {accent_ink};',
        f'--accent-soft: {accent_soft};',
        f'--c-accent: {accent};',
        f'--c-accent-hover: {accent_ink};',
        f'--c-chip: {accent_soft};',
        f'--c-coral: {accent};',
        f'--glow: color-mix(in srgb, {accent} 50%, transparent);',
    ]

    role_fallbacks = {
        'primary': fill_css_background(
            fill_type='gradient',
            gradient_start='#ff7a52',
            gradient_end=accent_ink or '#e04822',
            gradient_angle=145,
        ),
        'secondary': '#ffffff',
        'header': fill_css_background(
            fill_type='gradient',
            gradient_start='#ff7a52',
            gradient_end=accent_ink or '#e04822',
            gradient_angle=145,
        ),
        'modal': fill_css_background(
            fill_type='gradient',
            gradient_start='#ff7a52',
            gradient_end=accent_ink or '#e04822',
            gradient_angle=145,
        ),
    }

    for role, fallback in role_fallbacks.items():
        style = button_styles.get(role)
        bg = style.as_css_background(fallback=fallback) if style else fallback
        lines.append(f'--btn-{role}-bg: {escape(bg)};')

    return mark_safe('\n  '.join(lines))


def section_style_attr(block_styles: dict, page: str, section_key: str) -> str:
    style = block_styles.get(f'{page}.{section_key}')
    if style is None:
        return ''
    inline = style.section_inline_style()
    if not inline:
        return ''
    return mark_safe(f'style="{escape(inline)}"')


def button_style_attr(
    button_styles: dict,
    block_styles: dict,
    *,
    role: str = 'primary',
    page: str = '',
    section_key: str = '',
) -> str:
    bg = ''
    if page and section_key:
        section = block_styles.get(f'{page}.{section_key}')
        if section is not None and section.override_button_fill and section.has_custom_fill():
            bg = section.as_css_background()
    if not bg:
        style = button_styles.get(role)
        if style is not None:
            bg = style.as_css_background()
    if not bg:
        return ''
    return mark_safe(f'style="background: {escape(bg)};"')
