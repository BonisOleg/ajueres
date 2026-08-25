"""Hero image must stay Samarkand — never product/chili art."""

from __future__ import annotations

from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.core.management.commands.import_live_content import Command
from apps.core.models import SiteBlock

_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0c'
    b'IDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00'
    b'\x00IEND\xaeB`\x82'
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMARKAND = _REPO_ROOT / 'static' / 'img' / 'hero-samarkand.webp'


class HeroImageGuardTests(TestCase):
    def test_samarkand_static_asset_exists(self):
        self.assertTrue(_SAMARKAND.is_file(), f'missing {_SAMARKAND}')

    def test_import_hero_replaces_chili_with_samarkand(self):
        block, _ = SiteBlock.objects.get_or_create(page='home', key='hero_image')
        block.image.save(
            'hero-chill.png',
            SimpleUploadedFile('hero-chill.png', _PNG, content_type='image/png'),
            save=True,
        )
        Command()._hero_image(force=False)
        block.refresh_from_db()
        name = (block.image.name or '').lower()
        self.assertIn('samarkand', name)
        self.assertNotIn('chill', name)
        self.assertNotIn('illustration', name)
        self.assertNotIn('sensoy', name)

    def test_fix_hero_image_command_restores_samarkand_on_homepage(self):
        block, _ = SiteBlock.objects.get_or_create(page='home', key='hero_image')
        block.image.save(
            'hero-illustration.webp',
            SimpleUploadedFile(
                'hero-illustration.webp', _PNG, content_type='image/webp'
            ),
            save=True,
        )
        call_command('fix_hero_image')
        html = self.client.get(reverse('home')).content.decode().lower()
        self.assertIn('samarkand', html)
        self.assertNotIn('hero-illustration', html)
        self.assertNotIn('hero-chill', html)
