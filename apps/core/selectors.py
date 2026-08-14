"""Публічні селектори контенту та налаштувань (лише читання)."""

from __future__ import annotations

from django.core.cache import cache
from django.utils.translation import get_language

from .models import (
    AboutSection,
    Advantage,
    BlockStyle,
    CaseStudy,
    CompanyStat,
    LegalDocument,
    PartnerOffer,
    RetailPartner,
    SiteBlock,
    SiteButtonStyle,
    SiteSettings,
)

_VISIBLE_TRUTHY = frozenset({'1', 'true', 'yes', 'on'})
_CACHE_SETTINGS = 'site_settings'
_CACHE_BLOCKS_TTL = 60 * 10
_CACHE_RETAIL = 'retail_partners_public'
_CACHE_RETAIL_TTL = 60 * 10
_CACHE_BUTTONS = 'site_button_styles'
_CACHE_BLOCK_STYLES = 'block_styles_all'
_CACHE_THEME_TTL = 60 * 10


def get_site_settings() -> SiteSettings:
    cached = cache.get(_CACHE_SETTINGS)
    if cached is not None:
        return cached
    obj = SiteSettings.load()
    cache.set(_CACHE_SETTINGS, obj, timeout=60 * 30)
    return obj


def _blocks_cache_key(page: str, lang: str) -> str:
    return f'site_blocks:{page}:{lang}'


def get_blocks(page: str) -> dict[str, SiteBlock]:
    """Повертає {key: SiteBlock} для сторінки. Порожній dict, якщо блоків немає."""
    lang = get_language() or 'ru'
    cache_key = _blocks_cache_key(page, lang)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    blocks = {
        block.key: block
        for block in SiteBlock.objects.filter(page=page)
    }
    cache.set(cache_key, blocks, timeout=_CACHE_BLOCKS_TTL)
    return blocks


def get_block_text(blocks: dict[str, SiteBlock], key: str, default: str = '') -> str:
    """Текст блоку для поточної мови (modeltranslation). Fallback — gettext default."""
    from django.utils.translation import gettext as _

    block = blocks.get(key) if blocks else None
    if block is None:
        return _(default) if default else ''
    text = (block.text_html or '').strip()
    if text:
        return text
    return _(default) if default else ''


def get_block_image(blocks: dict[str, SiteBlock], key: str):
    block = blocks.get(key)
    if block is None or not block.image:
        return None
    return block.image


def is_section_visible(blocks: dict[str, SiteBlock], visibility_key: str) -> bool:
    """
    Visibility-ключі (*_visible): '1'/'true'/'yes'/'on' → True.
    Відсутній або порожній ключ → False (секція схована).
    """
    raw = get_block_text(blocks, visibility_key).lower()
    if not raw:
        return False
    return raw in _VISIBLE_TRUTHY


def get_advantages():
    return Advantage.objects.filter(is_active=True).order_by('order', 'id')


def get_company_stats():
    return CompanyStat.objects.filter(is_active=True).order_by('order', 'id')


def get_about_sections():
    """Активні секції з непорожнім body."""
    sections = AboutSection.objects.filter(is_active=True).order_by('order', 'id')
    return [s for s in sections if (s.body or '').strip()]


def get_partner_offers():
    return PartnerOffer.objects.filter(is_active=True).order_by('order', 'id')


def get_retail_partners() -> list[RetailPartner]:
    """Покупці (ритейл) для блоку «Наши партнёры» — media або static slug."""
    from apps.core.import_content_data import RETAIL_LOGO_STATIC

    cached_ids = cache.get(_CACHE_RETAIL)
    base = RetailPartner.objects.filter(is_active=True).order_by('order', 'name')
    if cached_ids is not None:
        by_id = {p.pk: p for p in base.filter(pk__in=cached_ids)}
        return [by_id[pk] for pk in cached_ids if pk in by_id]
    partners = [
        p
        for p in base
        if p.logo or (getattr(p, 'slug', '') in RETAIL_LOGO_STATIC)
    ]
    cache.set(_CACHE_RETAIL, [p.pk for p in partners], timeout=_CACHE_RETAIL_TTL)
    return partners


def invalidate_retail_partners_cache() -> None:
    cache.delete(_CACHE_RETAIL)


def get_case_studies():
    return CaseStudy.objects.filter(is_active=True).order_by('order', 'id')


def get_legal_document(slug: str) -> LegalDocument | None:
    return LegalDocument.objects.filter(slug=slug).first()


def get_privacy_policy() -> LegalDocument | None:
    return get_legal_document('privacy')


def invalidate_site_blocks_cache(page: str | None = None) -> None:
    """Скидає кеш блоків для всіх мов (викликати після save SiteBlock)."""
    langs = ('ru', 'uz', 'en')
    if page:
        pages = (page,)
    else:
        pages = SiteBlock.objects.values_list('page', flat=True).distinct()
    keys = [_blocks_cache_key(p, lang) for p in pages for lang in langs]
    if keys:
        cache.delete_many(keys)


def get_button_styles() -> dict[str, SiteButtonStyle]:
    cached = cache.get(_CACHE_BUTTONS)
    if cached is not None:
        return cached
    # Defaults лише в seed_site / admin — не INSERT на публічних запитах.
    styles = {obj.role: obj for obj in SiteButtonStyle.objects.all()}
    cache.set(_CACHE_BUTTONS, styles, timeout=_CACHE_THEME_TTL)
    return styles


def get_block_styles() -> dict[str, BlockStyle]:
    cached = cache.get(_CACHE_BLOCK_STYLES)
    if cached is not None:
        return cached
    styles = {
        obj.cache_key: obj
        for obj in BlockStyle.objects.all()
    }
    cache.set(_CACHE_BLOCK_STYLES, styles, timeout=_CACHE_THEME_TTL)
    return styles


def invalidate_theme_cache() -> None:
    cache.delete_many([_CACHE_BUTTONS, _CACHE_BLOCK_STYLES, _CACHE_SETTINGS])
