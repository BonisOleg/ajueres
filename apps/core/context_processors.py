from django.utils.translation import get_language, gettext_lazy as _

from apps.catalog import selectors as catalog_selectors

from .selectors import get_block_styles, get_button_styles, get_site_settings
from .theme_css import build_theme_root_css


def site_context(request):
    lang = getattr(request, 'LANGUAGE_CODE', None) or get_language() or 'ru'
    settings_obj = get_site_settings()
    button_styles = get_button_styles()
    block_styles = get_block_styles()
    return {
        'site_settings': settings_obj,
        'button_styles': button_styles,
        'block_styles': block_styles,
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
            {'url_name': 'home', 'label': _('Главная'), 'tone': 'coral'},
            {'url_name': 'products', 'label': _('Каталог'), 'tone': 'green'},
            {'url_name': 'about', 'label': _('О компании'), 'tone': 'blue'},
            {'url_name': 'contacts', 'label': _('Контакты'), 'tone': 'purple'},
        ),
        'nav_categories': list(catalog_selectors.get_categories()[:6]),
    }
