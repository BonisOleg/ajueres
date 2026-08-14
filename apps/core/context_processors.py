from django.utils.translation import get_language

from apps.catalog import selectors as catalog_selectors

from .button_preview import overlay_button_styles
from .legal_defaults import LEGAL_FALLBACK_TITLES
from .selectors import (
    get_block_styles,
    get_block_text,
    get_blocks,
    get_button_styles,
    get_legal_document,
    get_site_settings,
)
from .theme_css import build_theme_root_css


def site_context(request):
    lang = getattr(request, 'LANGUAGE_CODE', None) or get_language() or 'ru'
    settings_obj = get_site_settings()
    button_styles, button_preview = overlay_button_styles(request, get_button_styles())
    block_styles = get_block_styles()
    site_blocks = get_blocks('site')
    return {
        'site_settings': settings_obj,
        'button_styles': button_styles,
        'button_preview': button_preview,
        'block_styles': block_styles,
        'site_blocks': site_blocks,
        'theme_css_vars': build_theme_root_css(settings_obj, button_styles),
        'current_language': lang,
        'form_data': {},
        'form_errors': {},
        'ui_languages': (
            {'code': 'ru', 'label': 'RU'},
            {'code': 'uz', 'label': 'UZ'},
            {'code': 'en', 'label': 'EN'},
        ),
        'nav_items': (
            {
                'url_name': 'home',
                'label': get_block_text(site_blocks, 'nav_home', 'Главная'),
                'tone': 'coral',
            },
            {
                'url_name': 'products',
                'label': get_block_text(site_blocks, 'nav_catalog', 'Каталог'),
                'tone': 'green',
            },
            {
                'url_name': 'about',
                'label': get_block_text(site_blocks, 'nav_about', 'О компании'),
                'tone': 'blue',
            },
            {
                'url_name': 'contacts',
                'label': get_block_text(site_blocks, 'nav_contacts', 'Контакты'),
                'tone': 'purple',
            },
        ),
        'nav_categories': list(catalog_selectors.get_categories()[:6]),
        'legal_items': _legal_items(lang),
    }


def _legal_items(lang: str):
    code = (lang or 'ru')[:2]
    items = []
    for slug in ('privacy', 'offer'):
        doc = get_legal_document(slug)
        fallbacks = LEGAL_FALLBACK_TITLES[slug]
        label = (doc.title if doc and (doc.title or '').strip() else None) or fallbacks.get(
            code, fallbacks['ru']
        )
        items.append({'url_name': slug, 'slug': slug, 'label': label})
    return items
