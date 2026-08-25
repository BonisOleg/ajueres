"""Restore canonical homepage hero (Samarkand), remove wrong CMS uploads."""

from __future__ import annotations

from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.core.models import SiteBlock
from apps.core.selectors import invalidate_site_blocks_cache

_BAD_SUBSTRINGS = ('chill', 'hero-illustration', 'sensoy', 'hero-chill')


class Command(BaseCommand):
    help = (
        'Ensure home.hero_image is Samarkand (static/img/hero-samarkand.webp), '
        'replacing known-wrong product art uploads.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-only',
            action='store_true',
            help='Clear CMS image so the template static fallback is used',
        )

    def handle(self, *args, **options):
        block, _ = SiteBlock.objects.get_or_create(
            page='home', key='hero_image', defaults={'text_html': ''}
        )
        current = (block.image.name or '').lower() if block.image else ''
        is_wrong = any(bad in current for bad in _BAD_SUBSTRINGS)
        is_ok = 'samarkand' in current

        if options['clear_only']:
            if block.image:
                block.image.delete(save=False)
                block.image = None
                block.save(update_fields=['image'])
                invalidate_site_blocks_cache()
                self.stdout.write(self.style.SUCCESS('hero_image cleared'))
            else:
                self.stdout.write('hero_image already empty')
            return

        if is_ok and not is_wrong:
            self.stdout.write('hero_image already Samarkand — skip')
            return

        static_file = (
            Path(__file__).resolve().parents[4]
            / 'static'
            / 'img'
            / 'hero-samarkand.webp'
        )
        if not static_file.is_file():
            self.stderr.write(f'missing {static_file}')
            return

        if block.image:
            block.image.delete(save=False)
        block.image.save(
            'hero-samarkand.webp',
            ContentFile(static_file.read_bytes()),
            save=True,
        )
        invalidate_site_blocks_cache()
        self.stdout.write(
            self.style.SUCCESS(f'hero_image set from {static_file.name}')
        )
