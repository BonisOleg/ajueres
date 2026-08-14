"""Canonical, hreflang, robots meta, JSON-LD, robots.txt."""

from __future__ import annotations

import json
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponse
from django.urls import translate_url
from django.utils.translation import get_language, gettext as _

NOINDEX_QUERY_KEYS = frozenset({'page', 'q', 'category', 'brand', 'feature'})
OG_LOCALES = {
    'ru': 'ru_RU',
    'uz': 'uz_UZ',
    'en': 'en_US',
}
OG_IMAGE_PATH = 'img/logo-ajeres.png'
OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630
SITEMAP_URL_NAMES = (
    'home',
    'about',
    'products',
    'contacts',
    'privacy',
    'offer',
)


def public_site_url() -> str:
    raw = (getattr(settings, 'PUBLIC_SITE_URL', '') or 'https://ajeres.uz').strip()
    parsed = urlparse(raw if '://' in raw else f'https://{raw}')
    host = (parsed.hostname or 'ajeres.uz').removeprefix('www.')
    scheme = parsed.scheme or 'https'
    netloc = f'{host}:{parsed.port}' if parsed.port else host
    return f'{scheme}://{netloc}'


def organization_id() -> str:
    return f'{public_site_url()}#org'


def absolute_media_or_static(path: str) -> str:
    if path.startswith('http://') or path.startswith('https://'):
        return path
    return f'{public_site_url()}{path if path.startswith("/") else f"/{path}"}'


def _strip_default_lang_prefix(path: str, lang: str) -> str:
    default = settings.LANGUAGE_CODE
    if lang == default:
        if path == f'/{default}' or path == f'/{default}/':
            return '/'
        prefix = f'/{default}/'
        if path.startswith(prefix):
            return path[len(prefix) - 1 :]
    return path or '/'


def canonical_url(request) -> str:
    path = _strip_default_lang_prefix(request.path, get_language() or settings.LANGUAGE_CODE)
    if not path.startswith('/'):
        path = f'/{path}'
    return f'{public_site_url()}{path}'


def catalog_query_noindex(request) -> bool:
    for key in NOINDEX_QUERY_KEYS:
        if any((value or '').strip() for value in request.GET.getlist(key)):
            return True
    return False


def hreflang_entries(request) -> list[dict[str, str]]:
    path = request.path
    base = public_site_url()
    entries: list[dict[str, str]] = []
    default_abs = ''
    default_code = settings.LANGUAGE_CODE
    for code, _label in settings.LANGUAGES:
        translated = translate_url(path, code) or path
        translated = _strip_default_lang_prefix(translated, code)
        if not translated.startswith('/'):
            translated = f'/{translated}'
        abs_url = f'{base}{translated}'
        entries.append({'code': code, 'url': abs_url})
        if code == default_code:
            default_abs = abs_url
    entries.append({'code': 'x-default', 'url': default_abs})
    return entries


def _legal_title(url_name: str, document=None) -> str:
    from .legal_defaults import legal_display_title

    lang = (get_language() or settings.LANGUAGE_CODE)[:2]
    return legal_display_title(url_name, lang, document)


def page_meta(url_name: str | None, document=None) -> tuple[str, str]:
    if url_name in ('privacy', 'offer'):
        doc_title = _legal_title(url_name, document)
        title = f'{doc_title} — AJERES'
        suffix = _(
            'Официальный документ AJERES. Дистрибьютор продуктов питания в Узбекистане.'
        )
        return title, f'{doc_title}. {suffix}'
    mapping = {
        'home': (
            f"AJERES — {_('Дистрибьютор продуктов питания')}",
            _(
                'AJERES — импорт и дистрибуция продуктов питания в Узбекистане. '
                'Эксклюзивные бренды, логистика и вывод производителей на рынок. Свяжитесь с нами.'
            ),
        ),
        'products': (
            f"{_('Каталог')} — AJERES",
            _(
                'Каталог продуктов питания AJERES: соусы, снеки и бренды для ритейла '
                'в Узбекистане. Ассортимент дистрибьютора для партнёров и магазинов.'
            ),
        ),
        'about': (
            f"{_('О компании')} — AJERES",
            _(
                'О компании AJERES: дистрибьютор продуктов питания в Узбекистане с 2018 года. '
                'Импорт, логистика, продажи и развитие международных брендов.'
            ),
        ),
        'contacts': (
            f"{_('Контакты')} — AJERES",
            _(
                'Контакты AJERES в Узбекистане: телефон, адрес и форма заявки для ритейла '
                'и производителей. Свяжитесь с дистрибьютором продуктов питания.'
            ),
        ),
    }
    if url_name in mapping:
        return mapping[url_name]
    return (
        'AJERES',
        _('Дистрибьютор продуктов питания в Узбекистане'),
    )


def _postal_address(settings_obj) -> dict | None:
    street = ' '.join((settings_obj.address or '').split())
    if not street:
        return None
    return {
        '@type': 'PostalAddress',
        'streetAddress': street,
        'addressCountry': 'UZ',
    }


def _organization(settings_obj) -> dict:
    from django.templatetags.static import static

    org = {
        '@type': 'Organization',
        '@id': organization_id(),
        'name': settings_obj.company_name or 'AJERES',
        'url': public_site_url(),
        'logo': absolute_media_or_static(static(OG_IMAGE_PATH)),
    }
    if settings_obj.phone:
        org['telephone'] = settings_obj.phone
    if settings_obj.email:
        org['email'] = settings_obj.email
    address = _postal_address(settings_obj)
    if address:
        org['address'] = address
    return org


def _breadcrumb_label(url_name: str | None, document=None) -> str:
    if url_name in ('privacy', 'offer'):
        return _legal_title(url_name, document)
    labels = {
        'about': _('О компании'),
        'products': _('Каталог'),
        'contacts': _('Контакты'),
    }
    return labels.get(url_name or '', '')


def json_ld_graph(request, settings_obj, document=None) -> str:
    url_name = getattr(getattr(request, 'resolver_match', None), 'url_name', None)
    canonical = canonical_url(request)
    org = _organization(settings_obj)
    graph: list[dict] = [org]
    if url_name == 'home':
        graph.append(
            {
                '@type': 'WebSite',
                '@id': f'{public_site_url()}#website',
                'name': settings_obj.company_name or 'AJERES',
                'url': public_site_url(),
                'publisher': {'@id': organization_id()},
            }
        )
    if url_name == 'contacts':
        local: dict = {
            '@type': 'LocalBusiness',
            '@id': f'{public_site_url()}#local',
            'name': settings_obj.company_name or 'AJERES',
            'url': canonical,
            'parentOrganization': {'@id': organization_id()},
            'areaServed': {'@type': 'Country', 'name': 'Uzbekistan'},
        }
        if settings_obj.phone:
            local['telephone'] = settings_obj.phone
        if settings_obj.email:
            local['email'] = settings_obj.email
        address = _postal_address(settings_obj)
        if address:
            local['address'] = address
        graph.append(local)
    if url_name and url_name != 'home':
        current_name = _breadcrumb_label(url_name, document)
        if current_name:
            graph.append(
                {
                    '@type': 'BreadcrumbList',
                    'itemListElement': [
                        {
                            '@type': 'ListItem',
                            'position': 1,
                            'name': _('Главная'),
                            'item': f'{public_site_url()}/',
                        },
                        {
                            '@type': 'ListItem',
                            'position': 2,
                            'name': current_name,
                            'item': canonical,
                        },
                    ],
                }
            )
    payload = {'@context': 'https://schema.org', '@graph': graph}
    dumped = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    return dumped.replace('<', '\\u003c')


def build_seo_context(request, settings_obj) -> dict:
    url_name = getattr(getattr(request, 'resolver_match', None), 'url_name', None)
    document = None
    if url_name in ('privacy', 'offer'):
        from .selectors import get_legal_document

        document = get_legal_document(url_name)
    title, description = page_meta(url_name, document)
    lang = (get_language() or settings.LANGUAGE_CODE)[:2]
    from django.templatetags.static import static

    og_image = absolute_media_or_static(static(OG_IMAGE_PATH))
    noindex = catalog_query_noindex(request)
    return {
        'seo_title': title,
        'seo_description': description,
        'seo_canonical': canonical_url(request),
        'seo_hreflang': hreflang_entries(request),
        'seo_robots': 'noindex, follow' if noindex else '',
        'seo_og_locale': OG_LOCALES.get(lang, 'ru_RU'),
        'seo_og_locales_alt': [
            OG_LOCALES[code]
            for code, _ in settings.LANGUAGES
            if code != lang and code in OG_LOCALES
        ],
        'seo_og_image': og_image,
        'seo_og_image_width': OG_IMAGE_WIDTH,
        'seo_og_image_height': OG_IMAGE_HEIGHT,
        'seo_json_ld': json_ld_graph(request, settings_obj, document),
    }


def admin_disallow_path() -> str:
    slug = (settings.ADMIN_URL or '').strip('/')
    return f'/{slug}/'


def robots_txt(_request) -> HttpResponse:
    body = (
        'User-agent: *\n'
        f'Disallow: {admin_disallow_path()}\n'
        'Disallow: /i18n/\n'
        f'Sitemap: {public_site_url()}/sitemap.xml\n'
    )
    return HttpResponse(body, content_type='text/plain; charset=utf-8')


