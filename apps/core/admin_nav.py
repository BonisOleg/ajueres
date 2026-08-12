"""Unfold sidebar navigation for AJERES admin (Russian UI labels)."""

from __future__ import annotations

from django.urls import reverse_lazy

from .site_content_registry import build_content_sidebar_items


def build_navigation(request=None):
    return [
        {
            'title': 'Настройки',
            'separator': False,
            'items': [
                {
                    'title': 'Сайт',
                    'icon': 'settings',
                    'link': reverse_lazy('admin:core_sitesettings_changelist'),
                },
                {
                    'title': 'Стили кнопок',
                    'icon': 'palette',
                    'link': reverse_lazy('admin:core_sitebuttonstyle_changelist'),
                },
                {
                    'title': 'Стили секций',
                    'icon': 'format_paint',
                    'link': reverse_lazy('admin:core_blockstyle_changelist'),
                },
                {
                    'title': 'Сменить пароль',
                    'icon': 'lock_reset',
                    'link': reverse_lazy('admin:password_change'),
                },
            ],
        },
        {
            'title': 'Контент страниц',
            'separator': True,
            'items': build_content_sidebar_items(),
        },
        {
            'title': 'Контент',
            'separator': True,
            'items': [
                {
                    'title': 'Преимущества',
                    'icon': 'star',
                    'link': reverse_lazy('admin:core_advantage_changelist'),
                },
                {
                    'title': 'Цифры',
                    'icon': 'analytics',
                    'link': reverse_lazy('admin:core_companystat_changelist'),
                },
                {
                    'title': 'Секции «О компании»',
                    'icon': 'article',
                    'link': reverse_lazy('admin:core_aboutsection_changelist'),
                },
                {
                    'title': 'Предложения партнёрам',
                    'icon': 'handshake',
                    'link': reverse_lazy('admin:core_partneroffer_changelist'),
                },
                {
                    'title': 'Покупатели (ритейл)',
                    'icon': 'store',
                    'link': reverse_lazy('admin:core_retailpartner_changelist'),
                },
                {
                    'title': 'Кейсы',
                    'icon': 'emoji_events',
                    'link': reverse_lazy('admin:core_casestudy_changelist'),
                },
                {
                    'title': 'Правовые документы',
                    'icon': 'gavel',
                    'link': reverse_lazy('admin:core_legaldocument_changelist'),
                },
            ],
        },
        {
            'title': 'Каталог',
            'separator': True,
            'items': [
                {
                    'title': 'Категории',
                    'icon': 'category',
                    'link': reverse_lazy('admin:catalog_category_changelist'),
                },
                {
                    'title': 'Бренды',
                    'icon': 'sell',
                    'link': reverse_lazy('admin:catalog_brand_changelist'),
                },
                {
                    'title': 'Товары',
                    'icon': 'inventory_2',
                    'link': reverse_lazy('admin:catalog_product_changelist'),
                },
                {
                    'title': 'Фильтры товаров',
                    'icon': 'filter_alt',
                    'link': reverse_lazy('admin:catalog_productfilter_changelist'),
                },
            ],
        },
        {
            'title': 'Лиды',
            'separator': True,
            'items': [
                {
                    'title': 'Заявки',
                    'icon': 'inbox',
                    'link': reverse_lazy('admin:leads_contactinquiry_changelist'),
                },
            ],
        },
    ]
