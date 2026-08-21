"""Unfold sidebar: pages as groups, blocks as items (Russian labels)."""

from __future__ import annotations

from django.urls import reverse, reverse_lazy

from .site_content_registry import cms_sidebar_item
from .theme_fields import SECTION_STYLE_KEYS

_STYLE_PAGE_META = {
    'home': 'Главная',
    'products': 'Каталог',
    'about': 'О компании',
    'contacts': 'Контакты',
    'site': 'Сайт',
}

_STYLE_PAGE_ORDER = ('home', 'products', 'about', 'contacts', 'site')


def _model_item(title: str, icon: str, url_name: str) -> dict:
    return {
        'title': title,
        'icon': icon,
        'link': reverse_lazy(url_name),
    }


def _style_section_link(page: str, section_key: str):
    def _link(request=None):
        return reverse(
            'admin:core_blockstyle_section',
            args=[page, section_key],
        )

    return _link


def _style_section_active(page: str, section_key: str):
    def _active(request):
        path = getattr(request, 'path', '') or ''
        marker = f'/blockstyle/section/{page}/{section_key}/'
        if marker in path:
            return True
        if '/blockstyle/' not in path or '/change' not in path:
            return False
        return _current_block_style_key(request) == (page, section_key)

    return _active


def _current_block_style_key(request) -> tuple[str, str] | tuple[()]:
    cached = getattr(request, '_ajeres_block_style_key', None)
    if cached is not None:
        return cached
    try:
        from django.urls import resolve

        from .theme_models import BlockStyle

        match = resolve(request.path)
        object_id = match.kwargs.get('object_id')
        if not object_id:
            request._ajeres_block_style_key = ()
            return ()
        pair = (
            BlockStyle.objects.filter(pk=object_id)
            .values_list('page', 'section_key')
            .first()
        )
        request._ajeres_block_style_key = pair or ()
    except Exception:
        request._ajeres_block_style_key = ()
    return request._ajeres_block_style_key


def _style_short_label(label: str) -> str:
    if ' — ' in label:
        return label.split(' — ', 1)[1]
    return label


def _style_page_groups() -> list[dict]:
    by_page: dict[str, list[tuple[str, str]]] = {}
    for page, key, label in SECTION_STYLE_KEYS:
        by_page.setdefault(page, []).append((key, label))

    groups = [
        {
            'title': 'Стили',
            'separator': True,
            'collapsible': True,
            'items': [
                _model_item(
                    'Кнопки',
                    'palette',
                    'admin:core_sitebuttonstyle_changelist',
                ),
            ],
        }
    ]
    for page in _STYLE_PAGE_ORDER:
        sections = by_page.get(page)
        if not sections:
            continue
        title = _STYLE_PAGE_META.get(page, page)
        groups.append(
            {
                'title': f'Стили · {title}',
                'separator': False,
                'collapsible': True,
                'items': [
                    {
                        'title': _style_short_label(label),
                        'icon': 'format_paint',
                        'link': _style_section_link(page, key),
                        'active': _style_section_active(page, key),
                    }
                    for key, label in sections
                ],
            }
        )
    return groups


def build_navigation(request=None):
    return [
        {
            'title': 'Обзор',
            'separator': False,
            'items': [
                {
                    'title': 'Последние действия',
                    'icon': 'history',
                    'link': reverse_lazy('admin:recent_actions'),
                },
            ],
        },
        {
            'title': 'Настройки',
            'separator': False,
            'items': [
                _model_item('Сайт', 'settings', 'admin:core_sitesettings_changelist'),
                cms_sidebar_item('site', 'header'),
                cms_sidebar_item('site', 'footer'),
                _model_item(
                    'Правовые документы',
                    'gavel',
                    'admin:core_legaldocument_changelist',
                ),
                {
                    'title': 'Сменить пароль',
                    'icon': 'lock_reset',
                    'link': reverse_lazy('admin:password_change'),
                },
            ],
        },
        {
            'title': 'Главная',
            'separator': True,
            'collapsible': True,
            'items': [
                cms_sidebar_item('home', 'hero'),
                _model_item('Цифры', 'analytics', 'admin:core_companystat_changelist'),
                cms_sidebar_item('home', 'advantages'),
                _model_item(
                    'Карточки преимуществ',
                    'stars',
                    'admin:core_advantage_changelist',
                ),
                cms_sidebar_item('home', 'coop'),
                cms_sidebar_item('home', 'brands'),
                _model_item(
                    'Покупатели (ритейл)',
                    'store',
                    'admin:core_retailpartner_changelist',
                ),
                _model_item('Кейсы', 'emoji_events', 'admin:core_casestudy_changelist'),
                cms_sidebar_item('home', 'cta'),
            ],
        },
        {
            'title': 'Каталог',
            'separator': False,
            'collapsible': True,
            'items': [
                _model_item(
                    'Фильтры',
                    'filter_alt',
                    'admin:catalog_productfilter_changelist',
                ),
            ],
        },
        {
            'title': 'О компании',
            'separator': False,
            'collapsible': True,
            'items': [
                cms_sidebar_item('about', 'about'),
                _model_item('Цифры', 'analytics', 'admin:core_companystat_changelist'),
                _model_item(
                    'Секции',
                    'article',
                    'admin:core_aboutsection_changelist',
                ),
            ],
        },
        {
            'title': 'Контакты',
            'separator': False,
            'collapsible': True,
            'items': [
                cms_sidebar_item('contacts', 'contacts'),
                _model_item(
                    'Предложения партнёрам',
                    'handshake',
                    'admin:core_partneroffer_changelist',
                ),
            ],
        },
        *_style_page_groups(),
        {
            'title': 'Каталог товаров',
            'separator': True,
            'items': [
                _model_item('Товары', 'inventory_2', 'admin:catalog_product_changelist'),
                _model_item('Категории', 'category', 'admin:catalog_category_changelist'),
                _model_item('Бренды', 'sell', 'admin:catalog_brand_changelist'),
            ],
        },
        {
            'title': 'Лиды',
            'separator': True,
            'items': [
                _model_item('Заявки', 'inbox', 'admin:leads_contactinquiry_changelist'),
            ],
        },
    ]


def iter_nav_items(navigation=None):
    """Flatten sidebar items including nested folders (tests / search)."""
    groups = navigation if navigation is not None else build_navigation()
    stack = [item for group in groups for item in group.get('items', [])]
    while stack:
        item = stack.pop(0)
        yield item
        children = item.get('items')
        if isinstance(children, list):
            stack[0:0] = children
