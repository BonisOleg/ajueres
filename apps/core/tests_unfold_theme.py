"""Unfold light branding: colors, logo, favicons, default theme."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.unfold_theme import (
    UNFOLD_COLORS,
    admin_scripts,
    admin_styles,
    site_favicons,
    site_logo,
    unfold_colors,
)


class UnfoldThemeConfigTests(SimpleTestCase):
    def test_brand_colors(self):
        colors = unfold_colors()
        self.assertEqual(colors['primary']['500'], '#ff5a36')
        self.assertEqual(colors['base']['900'], '#0f1835')
        self.assertEqual(colors['green']['500'], '#1fa968')
        self.assertEqual(colors['blue']['500'], '#3e7bfa')
        self.assertIsNot(colors['primary'], UNFOLD_COLORS['primary'])

    def test_settings_wire_callables(self):
        unfold = settings.UNFOLD
        self.assertEqual(unfold['SITE_LOGO'], 'apps.core.unfold_theme.site_logo')
        self.assertNotIn('SITE_ICON', unfold)
        self.assertEqual(unfold['SITE_FAVICONS'], 'apps.core.unfold_theme.site_favicons')
        self.assertEqual(unfold['COLORS'], 'apps.core.unfold_theme.unfold_colors')
        self.assertNotIn('THEME', unfold)
        self.assertIn('apps.core.unfold_theme.admin_styles', unfold['STYLES'])
        self.assertIn('apps.core.unfold_theme.admin_scripts', unfold['SCRIPTS'])
        self.assertNotEqual(unfold.get('SITE_HEADER'), 'AJERES — Админ-панель')

    def test_logo_and_favicons_point_to_mark(self):
        logo = site_logo()
        self.assertIn('favicon.png', logo)
        hrefs = [item['href'] for item in site_favicons()]
        self.assertTrue(any('favicon.png' in href for href in hrefs))
        self.assertTrue(admin_styles().endswith('css/admin/unfold_theme.css'))
        self.assertTrue(admin_scripts().endswith('js/admin/unfold_default_light.js'))


class UnfoldAdminBrandingTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'owner',
            'owner@ajeres.uz',
            'OldPass123!',
        )
        self.client.force_login(self.user)

    def test_admin_index_uses_logo_and_light_assets(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('img/icons/favicon.png', content)
        self.assertIn('css/admin/unfold_theme.css', content)
        self.assertIn('js/admin/unfold_default_light.js', content)
        self.assertEqual(content.count('class="admin-brand-logo"'), 1)
        self.assertEqual(content.count('<img src="/static/img/icons/favicon.png"'), 1)
        self.assertIn('admin-theme-switch', content)
        self.assertNotIn('AJERES — Админ-панель', content)
        self.assertIn('--color-primary-500: rgb(255, 90, 54)', content)
