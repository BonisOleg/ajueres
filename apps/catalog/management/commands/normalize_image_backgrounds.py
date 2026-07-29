"""Replace dark catalog image backgrounds with light (#f7f7f7)."""

from __future__ import annotations

from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.image_utils import replace_dark_background
from apps.catalog.models import Brand, Product
from apps.core.models import RetailPartner, SiteBlock


class Command(BaseCommand):
    help = 'Normalize dark image backgrounds to light for catalog and CMS images'

    def handle(self, *args, **options):
        updated = 0
        updated += self._process_products()
        updated += self._process_brands()
        updated += self._process_retail_partners()
        updated += self._process_hero()
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} image(s)'))

    def _normalize_field(self, obj, field_name: str, label: str) -> int:
        field = getattr(obj, field_name)
        if not field or not getattr(field, 'name', None):
            return 0
        path = Path(field.path)
        if not path.is_file():
            return 0

        raw = path.read_bytes()
        processed = replace_dark_background(raw)
        if processed == raw:
            return 0

        stem = Path(field.name).stem
        field.save(f'{stem}.png', ContentFile(processed), save=False)
        obj.save(update_fields=[field_name])
        self.stdout.write(f'  {label}')
        return 1

    def _process_products(self) -> int:
        count = 0
        for product in Product.objects.exclude(image=''):
            count += self._normalize_field(
                product, 'image', f'product {product.name}'
            )
        return count

    def _process_brands(self) -> int:
        count = 0
        for brand in Brand.objects.exclude(logo=''):
            count += self._normalize_field(brand, 'logo', f'brand {brand.name}')
        return count

    def _process_retail_partners(self) -> int:
        count = 0
        for partner in RetailPartner.objects.exclude(logo=''):
            count += self._normalize_field(
                partner, 'logo', f'retail {partner.name}'
            )
        return count

    def _process_hero(self) -> int:
        count = 0
        block = SiteBlock.objects.filter(page='home', key='hero_image').first()
        if block and block.image:
            count += self._normalize_field(block, 'image', 'hero image')
        return count
