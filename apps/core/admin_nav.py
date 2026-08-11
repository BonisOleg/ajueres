"""Unfold sidebar navigation for AJERES admin."""

from __future__ import annotations

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .site_content_registry import build_content_sidebar_items


def build_navigation(request=None):
    return [
        {
            'title': _('Налаштування'),
            'separator': False,
            'items': [
                {
                    'title': _('Сайт'),
                    'icon': 'settings',
                    'link': reverse_lazy('admin:core_sitesettings_changelist'),
                },
                {
                    'title': _('Стилі кнопок'),
                    'icon': 'palette',
                    'link': reverse_lazy('admin:core_sitebuttonstyle_changelist'),
                },
                {
                    'title': _('Стилі секцій'),
                    'icon': 'format_paint',
                    'link': reverse_lazy('admin:core_blockstyle_changelist'),
                },
            ],
        },
        {
            'title': _('Контент сторінок'),
            'separator': True,
            'items': build_content_sidebar_items(),
        },
        {
            'title': _('Контент'),
            'separator': True,
            'items': [
                {
                    'title': _('Переваги'),
                    'icon': 'star',
                    'link': reverse_lazy('admin:core_advantage_changelist'),
                },
                {
                    'title': _('Цифри'),
                    'icon': 'analytics',
                    'link': reverse_lazy('admin:core_companystat_changelist'),
                },
                {
                    'title': _('Секції «Про компанію»'),
                    'icon': 'article',
                    'link': reverse_lazy('admin:core_aboutsection_changelist'),
                },
                {
                    'title': _('Пропозиції партнерам'),
                    'icon': 'handshake',
                    'link': reverse_lazy('admin:core_partneroffer_changelist'),
                },
                {
                    'title': _('Покупці (ритейл)'),
                    'icon': 'store',
                    'link': reverse_lazy('admin:core_retailpartner_changelist'),
                },
                {
                    'title': _('Кейси'),
                    'icon': 'emoji_events',
                    'link': reverse_lazy('admin:core_casestudy_changelist'),
                },
                {
                    'title': _('Правові документи'),
                    'icon': 'gavel',
                    'link': reverse_lazy('admin:core_legaldocument_changelist'),
                },
            ],
        },
        {
            'title': _('Каталог'),
            'separator': True,
            'items': [
                {
                    'title': _('Категорії'),
                    'icon': 'category',
                    'link': reverse_lazy('admin:catalog_category_changelist'),
                },
                {
                    'title': _('Бренди'),
                    'icon': 'sell',
                    'link': reverse_lazy('admin:catalog_brand_changelist'),
                },
                {
                    'title': _('Товари'),
                    'icon': 'inventory_2',
                    'link': reverse_lazy('admin:catalog_product_changelist'),
                },
            ],
        },
        {
            'title': _('Ліди'),
            'separator': True,
            'items': [
                {
                    'title': _('Заявки'),
                    'icon': 'inbox',
                    'link': reverse_lazy('admin:leads_contactinquiry_changelist'),
                },
            ],
        },
    ]
