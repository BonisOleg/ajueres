"""Admin sidebar: pages as groups, blocks as items, styles by page."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.admin_nav import build_navigation, iter_nav_items
from apps.core.theme_models import BlockStyle


def _group_titles(navigation) -> list[str]:
    return [group['title'] for group in navigation]


def _child_titles(group: dict) -> list[str]:
    return [item['title'] for item in group.get('items') or []]


def _group(navigation, title: str) -> dict:
    return next(group for group in navigation if group['title'] == title)


class NestedAdminNavTests(SimpleTestCase):
    def test_page_groups_exist(self):
        titles = _group_titles(build_navigation())
        self.assertIn('Главная', titles)
        self.assertIn('Каталог', titles)
        self.assertIn('О компании', titles)
        self.assertIn('Контакты', titles)
        self.assertIn('Стили', titles)
        self.assertIn('Стили · Главная', titles)
        self.assertIn('Каталог товаров', titles)
        self.assertNotIn('Контент страниц', titles)

    def test_home_blocks_are_under_home_group(self):
        home = _group(build_navigation(), 'Главная')
        titles = _child_titles(home)
        self.assertIn('Hero', titles)
        self.assertIn('Цифры', titles)
        self.assertIn('Карточки преимуществ', titles)
        self.assertIn('Кейсы', titles)
        self.assertNotIn('Главная — Hero', titles)

    def test_filters_live_under_catalog_page_not_products(self):
        nav = build_navigation()
        catalog = _group(nav, 'Каталог')
        self.assertEqual(_child_titles(catalog), ['Фильтры'])

        products = _group(nav, 'Каталог товаров')
        self.assertEqual(
            _child_titles(products),
            ['Товары', 'Категории', 'Бренды'],
        )
        self.assertNotIn('Фильтры', _child_titles(products))
        self.assertNotIn('Фильтры товаров', _child_titles(products))

    def test_styles_grouped_by_page(self):
        nav = build_navigation()
        self.assertEqual(_child_titles(_group(nav, 'Стили')), ['Кнопки'])
        home_styles = _group(nav, 'Стили · Главная')
        self.assertIn('Hero', _child_titles(home_styles))
        self.assertIn('Преимущества', _child_titles(home_styles))

    def test_about_contacts_and_chrome(self):
        nav = build_navigation()
        self.assertIn('Секции', _child_titles(_group(nav, 'О компании')))
        self.assertIn(
            'Предложения партнёрам',
            _child_titles(_group(nav, 'Контакты')),
        )
        settings = _group(nav, 'Настройки')
        self.assertIn('Шапка', _child_titles(settings))
        self.assertIn('Подвал', _child_titles(settings))

    def test_iter_nav_items_includes_nested(self):
        titles = [item['title'] for item in iter_nav_items()]
        self.assertIn('Hero', titles)
        self.assertIn('Фильтры', titles)
        self.assertIn('Товары', titles)


class BlockStyleSectionRedirectTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'owner',
            'owner@ajeres.uz',
            'OldPass123!',
        )
        self.client.force_login(self.user)
        BlockStyle.ensure_defaults()

    def test_section_url_redirects_to_change(self):
        obj = BlockStyle.objects.get(page='home', section_key='hero')
        response = self.client.get(
            reverse('admin:core_blockstyle_section', args=['home', 'hero'])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('admin:core_blockstyle_change', args=[obj.pk]),
        )

    def test_admin_index_renders_page_groups(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Каталог товаров', content)
        self.assertIn('Фильтры', content)
        self.assertIn('Стили · Главная', content)
        self.assertNotIn('Контент страниц', content)
        sidebar = content.split('id="nav-sidebar-inner"', 1)[-1].split('id="main"', 1)[0]
        self.assertIn('Hero', sidebar)
        self.assertNotIn('Главная — Hero', sidebar)
