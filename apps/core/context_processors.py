from django.utils.translation import get_language, gettext_lazy as _

from apps.catalog import selectors as catalog_selectors

from .selectors import get_site_settings


def site_context(request):
    lang = getattr(request, 'LANGUAGE_CODE', None) or get_language() or 'ru'
    return {
        'site_settings': get_site_settings(),
        'current_language': lang,
        'form_data': {},
        'form_errors': {},
        'ui_languages': (
            {'code': 'uz', 'label': 'UZ'},
            {'code': 'en', 'label': 'EN'},
            {'code': 'ru', 'label': 'RU'},
        ),
        'nav_items': (
            {'url_name': 'home', 'label': _('Главная'), 'tone': 'coral'},
            {'url_name': 'products', 'label': _('Каталог'), 'tone': 'green'},
            {'url_name': 'about', 'label': _('О компании'), 'tone': 'blue'},
            {'url_name': 'contacts', 'label': _('Контакты'), 'tone': 'purple'},
        ),
        'nav_categories': list(catalog_selectors.get_categories()[:6]),
    }
