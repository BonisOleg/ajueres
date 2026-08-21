"""Recent actions page + product media URL / Vercel MediaBlob persistence."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.core.admin_nav import build_navigation, iter_nav_items
from apps.core.admin_site_content_widgets import file_preview_url
from apps.core.media_models import MediaBlob
from apps.core.media_serve import serve_media
from apps.core.templatetags.ajeres_tags import product_image_url
from apps.core.webp_storage import WebPFileSystemStorage


def _group(navigation, title: str) -> dict:
    return next(group for group in navigation if group['title'] == title)


def _tiny_png() -> ContentFile:
    buf = BytesIO()
    Image.new('RGB', (8, 8), (20, 120, 40)).save(buf, format='PNG')
    return ContentFile(buf.getvalue(), name='tiny.png')


class RecentActionsAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'owner',
            'owner@ajeres.uz',
            'OldPass123!',
        )
        self.client.force_login(self.user)

    def test_sidebar_has_recent_actions_item(self):
        overview = _group(build_navigation(), 'Обзор')
        titles = [item['title'] for item in overview.get('items') or []]
        self.assertIn('Последние действия', titles)
        links = [
            str(item.get('link') or '')
            for item in iter_nav_items(build_navigation())
        ]
        self.assertIn(reverse('admin:recent_actions'), links)

    def test_index_hides_recent_actions_module(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn('id="recent-actions-module"', content)
        self.assertNotIn('id="content-related"', content)

    def test_recent_actions_page_lists_entries(self):
        ct = ContentType.objects.get_for_model(self.user)
        LogEntry.objects.log_action(
            user_id=self.user.pk,
            content_type_id=ct.pk,
            object_id=str(self.user.pk),
            object_repr='test-action-object',
            action_flag=CHANGE,
        )
        response = self.client.get(reverse('admin:recent_actions'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('id="recent-actions-page"', content)
        self.assertIn('test-action-object', content)
        self.assertIn('Последние действия', content)


class ProductImageUrlTests(SimpleTestCase):
    def test_prefers_existing_media_over_static_map(self):
        storage = SimpleNamespace(exists=lambda name: True)
        image = SimpleNamespace(
            name='catalog/products/custom.webp',
            url='/media/catalog/products/custom.webp',
            storage=storage,
        )
        product = SimpleNamespace(slug='riceup-tortilla-salt-60', image=image)
        self.assertEqual(
            product_image_url(product),
            '/media/catalog/products/custom.webp',
        )

    def test_falls_back_to_static_when_media_missing(self):
        storage = SimpleNamespace(exists=lambda name: False)
        image = SimpleNamespace(
            name='catalog/products/missing.webp',
            url='/media/catalog/products/missing.webp',
            storage=storage,
        )
        product = SimpleNamespace(slug='sen-soy-somen-noodle-300-1', image=image)
        url = product_image_url(product)
        self.assertIn('img/catalog/', url)


class FilePreviewUrlTests(SimpleTestCase):
    def test_returns_empty_when_storage_missing_file(self):
        storage = SimpleNamespace(exists=lambda name: False)
        value = SimpleNamespace(
            name='catalog/products/gone.webp',
            url='/media/catalog/products/gone.webp',
            storage=storage,
        )
        self.assertEqual(file_preview_url(value), '')


@override_settings(IS_VERCEL=True)
class MediaBlobStorageTests(TestCase):
    def test_save_persists_blob_and_serve_after_disk_delete(self):
        from django.conf import settings

        self.assertTrue(settings.IS_VERCEL)
        storage = WebPFileSystemStorage()
        name = storage.save('catalog/products/blob-test.png', _tiny_png())
        self.assertTrue(MediaBlob.objects.filter(path=name).exists())

        path = Path(storage.path(name))
        self.assertTrue(path.is_file())
        path.unlink()
        self.assertFalse(path.is_file())

        self.assertTrue(storage.exists(name))
        request = RequestFactory().get(f'/media/{name}')
        response = serve_media(request, path=name)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) > 0)
