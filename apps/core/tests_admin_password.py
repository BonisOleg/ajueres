"""Admin password-change menu and superuser seed behaviour."""

from __future__ import annotations

import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.admin_nav import iter_nav_items
from apps.core.ensure_superuser import ensure_default_superuser


class AdminPasswordNavTests(SimpleTestCase):
    def test_sidebar_has_password_change_item(self):
        items = list(iter_nav_items())
        titles = [item['title'] for item in items]
        self.assertIn('Сменить пароль', titles)
        links = [
            str(item['link'])
            for item in items
            if item.get('link') is not None and not callable(item.get('link'))
        ]
        self.assertIn(reverse('admin:password_change'), links)


class EnsureSuperuserPasswordTests(TestCase):
    @patch.dict(
        os.environ,
        {
            'DJANGO_SUPERUSER_USERNAME': 'owner',
            'DJANGO_SUPERUSER_PASSWORD': 'FirstPass123!',
            'DJANGO_SUPERUSER_EMAIL': 'owner@ajeres.uz',
        },
    )
    def test_does_not_reset_password_on_second_call(self):
        User = get_user_model()
        ensure_default_superuser()
        user = User.objects.get(username='owner')
        user.set_password('OwnerNewPass456!')
        user.save()

        username, created = ensure_default_superuser()

        self.assertEqual(username, 'owner')
        self.assertFalse(created)
        user.refresh_from_db()
        self.assertTrue(user.check_password('OwnerNewPass456!'))
        self.assertFalse(user.check_password('FirstPass123!'))


class AdminUserMenuTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'owner',
            'owner@ajeres.uz',
            'OldPass123!',
        )
        self.client.force_login(self.user)

    def test_plaque_menu_has_site_themes_and_password(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('admin-user-menu__trigger', content)
        self.assertIn('openUserLinks = !openUserLinks', content)
        self.assertIn('Открыть сайт', content)
        self.assertIn('Сменить пароль', content)
        self.assertIn(reverse('admin:password_change'), content)
        self.assertIn('Светлая', content)
        self.assertIn('Тёмная', content)
        self.assertIn('admin-user-menu__panel', content)


class AdminPasswordChangeViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'owner',
            'owner@ajeres.uz',
            'OldPass123!',
        )
        self.client.force_login(self.user)

    def test_get_form(self):
        response = self.client.get(reverse('admin:password_change'))
        self.assertEqual(response.status_code, 200)

    def test_post_changes_password(self):
        response = self.client.post(
            reverse('admin:password_change'),
            {
                'old_password': 'OldPass123!',
                'new_password1': 'NewPass456!',
                'new_password2': 'NewPass456!',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass456!'))
