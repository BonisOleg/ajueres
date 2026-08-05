from pathlib import Path
from urllib.parse import urlencode

import json

from django import template
from django.template.defaultfilters import linebreaks
from django.templatetags.static import static
from django.urls import reverse, translate_url
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import check_for_language

from apps.core.selectors import get_block_image, get_block_text

register = template.Library()

ADVANTAGE_IMAGES = {
    'assortment': 'img/advantages/assortment.png',
    'brands': 'img/advantages/brands.png',
    'logistics': 'img/advantages/logistics.png',
    'terms': 'img/advantages/terms.png',
    'experience': 'img/advantages/experience.png',
    'analytics': 'img/advantages/analytics.png',
}

_CATALOG_STATIC_MAP: dict[str, str] | None = None
_CATALOG_JSON = (
    Path(__file__).resolve().parents[3] / 'content' / 'catalog_products.json'
)


def _catalog_static_map() -> dict[str, str]:
    global _CATALOG_STATIC_MAP
    if _CATALOG_STATIC_MAP is None:
        try:
            rows = json.loads(_CATALOG_JSON.read_text(encoding='utf-8'))
            _CATALOG_STATIC_MAP = {
                row['slug']: row['static_image']
                for row in rows
                if row.get('slug') and row.get('static_image')
            }
        except (OSError, json.JSONDecodeError, TypeError, KeyError):
            _CATALOG_STATIC_MAP = {}
    return _CATALOG_STATIC_MAP


@register.simple_tag
def product_image_url(product):
    """Prefer shipped static catalog images (Vercel-safe), else media."""
    static_name = _catalog_static_map().get(getattr(product, 'slug', '') or '')
    if static_name:
        return static(f'img/catalog/{static_name}')
    image = getattr(product, 'image', None)
    if image:
        try:
            return image.url
        except ValueError:
            return ''
    return ''


@register.simple_tag(takes_context=True)
def change_language_url(context, lang_code):
    """Поточний URL з префіксом мови (для перемикачів RU/UZ/EN)."""
    request = context.get('request')
    if not request or not check_for_language(lang_code):
        return f'/{lang_code}/'
    translated = translate_url(request.get_full_path(), lang_code)
    return translated or f'/{lang_code}/'


@register.simple_tag
def block_text(blocks, key, default=''):
    return get_block_text(blocks or {}, key, default)


@register.simple_tag
def block_text_br(blocks, key, default=''):
    text = get_block_text(blocks or {}, key, default)
    return mark_safe(linebreaks(escape(text)))


@register.simple_tag
def block_image(blocks, key):
    return get_block_image(blocks or {}, key)


@register.filter(needs_autoescape=True)
def break_before_street(value, autoescape=True):
    """Перенос рядка перед «ул.» / street markers в адресі."""
    if value is None:
        return ''
    text = str(value)
    markers = (' ул.', ' ko‘cha', " ko'cha", ' st.', ' street')
    for marker in markers:
        idx = text.find(marker)
        if idx == -1:
            continue
        left = text[:idx].rstrip(' ,')
        right = text[idx + 1 :].lstrip()
        if autoescape:
            left = escape(left)
            right = escape(right)
        return mark_safe(f'{left},<br>{right}')
    return escape(text) if autoescape else text


@register.simple_tag
def advantage_icon(icon_key):
    key = icon_key or 'assortment'
    path = ADVANTAGE_IMAGES.get(key, ADVANTAGE_IMAGES['assortment'])
    url = escape(static(path))
    return mark_safe(
        f'<img src="{url}" alt="" width="184" height="184" '
        f'loading="lazy" decoding="async">'
    )


@register.simple_tag(takes_context=True)
def catalog_filter_url(
    context,
    *,
    toggle_category=None,
    clear_categories=False,
    page=None,
):
    """
    URL каталогу зі збереженням brand/q і toggle category (OR multi-select).
    clear_categories=True — «Все».
    """
    categories = list(context.get('active_categories') or [])
    brand = context.get('active_brand') or ''
    search_q = context.get('search_q') or ''

    if clear_categories:
        categories = []
    elif toggle_category:
        slug = str(toggle_category).strip()
        if slug in categories:
            categories = [item for item in categories if item != slug]
        elif slug:
            categories = [*categories, slug]

    params: list[tuple[str, str]] = [('category', slug) for slug in categories]
    if brand:
        params.append(('brand', brand))
    if search_q:
        params.append(('q', search_q))
    if page not in (None, '', 1, '1'):
        params.append(('page', str(page)))

    base = reverse('products')
    if not params:
        return base
    return f'{base}?{urlencode(params)}'
