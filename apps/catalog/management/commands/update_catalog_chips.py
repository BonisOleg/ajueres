"""Remove tea catalog; add chips category and products from supplier zip.

Idempotent: safe to re-run. Uses get_or_create by product slug.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.models import Brand, Category, Product
from apps.catalog.selectors import invalidate_catalog_list_cache

DEFAULT_ZIP = Path.home() / 'Downloads' / 'Чипсы.zip'

# (brand_slug, slug, name_ru, name_en, package, zip_member_suffix)
# zip_member_suffix is matched against ZipInfo.filename (UTF-8 fixed)
CHIPS_PRODUCTS = [
    # RICEUP — brown rice chips
    (
        'riceup',
        'riceup-rice-chips-barbecue-60',
        'Рисовые чипсы «Barbecue»',
        'Brown Rice Chips «Barbecue»',
        '60 гр.',
        'RICEUP/rice-up-rice-chips-barbecue-60g-8lang-flexo-mock-up-small-1-768x768.png',
    ),
    (
        'riceup',
        'riceup-rice-chips-cheese-60',
        'Рисовые чипсы «Cheese»',
        'Brown Rice Chips «Cheese»',
        '60 гр.',
        'RICEUP/rice-up-rice-chips-cheese-60g-8lang-flexo-mock-up-small-768x768.png',
    ),
    (
        'riceup',
        'riceup-rice-chips-hot-chili-60',
        'Рисовые чипсы «Hot Chili Pepper»',
        'Brown Rice Chips «Hot Chili Pepper»',
        '60 гр.',
        'RICEUP/rice-up-rice-chips-hot-chili-peper-60g-flexo-mock-up-768x768.png',
    ),
    (
        'riceup',
        'riceup-rice-chips-ketchup-60',
        'Рисовые чипсы «Ketchup»',
        'Brown Rice Chips «Ketchup»',
        '60 гр.',
        'RICEUP/rice-up-rice-chips-ketchup-60g-flexo-mock-up-small-768x768.png',
    ),
    (
        'riceup',
        'riceup-rice-chips-sea-salt-60',
        'Рисовые чипсы «Sea Salt»',
        'Brown Rice Chips «Sea Salt»',
        '60 гр.',
        'RICEUP/rice-up-rice-chips-sea-salt-60g-flexo-mock-up-small-res-768x768.png',
    ),
    (
        'riceup',
        'riceup-rice-chips-sour-cream-onion-60',
        'Рисовые чипсы «Sour Cream & Onion»',
        'Brown Rice Chips «Sour Cream & Onion»',
        '60 гр.',
        'RICEUP/rice-up-rice-chips-sour-cream-and-onion-60g-8lang-flexo-mock-up-small-768x768.png',
    ),
    # RICEUP — tortilla chips (folder TORTILA in zip)
    (
        'riceup',
        'riceup-tortilla-black-olives-60',
        'Тортилья-чипсы «Black Olives & Sundried Tomatoes»',
        'Tortilla Chips «Black Olives & Sundried Tomatoes»',
        '60 гр.',
        'TORTILA/04641_tortilla-chips_mat_black_olives_60gr-768x768.jpg',
    ),
    (
        'riceup',
        'riceup-tortilla-nacho-cheese-60',
        'Тортилья-чипсы «Nacho Cheese & Jalapeño»',
        'Tortilla Chips «Nacho Cheese & Juicy Jalapeños»',
        '60 гр.',
        'TORTILA/04641_tortilla-chips_mat_nacho_cheese_60gr-768x768.jpg',
    ),
    (
        'riceup',
        'riceup-tortilla-salt-60',
        'Тортилья-чипсы «Salt»',
        'Tortilla Chips «Salt»',
        '60 гр.',
        'TORTILA/04641_tortilla-chips_mat_salt_60gr-768x768.jpg',
    ),
    (
        'riceup',
        'riceup-tortilla-sour-cream-onion-60',
        'Тортилья-чипсы «Sour Cream & Green Onion»',
        'Tortilla Chips «Sour Cream & Green Onion»',
        '60 гр.',
        'TORTILA/04641_tortilla-chips_mat_sour_cream_green_onion_60gr-1-768x768.jpg',
    ),
    (
        'riceup',
        'riceup-tortilla-texas-bbq-60',
        'Тортилья-чипсы «Texas Style BBQ»',
        'Tortilla Chips «Texas Style BBQ»',
        '60 гр.',
        'TORTILA/04641_tortilla-chips_mat_texas_style_bbq_60gr-768x768.jpg',
    ),
    (
        'riceup',
        'riceup-tortilla-yellow-cheddar-60',
        'Тортилья-чипсы «Yellow Cheddar»',
        'Tortilla Chips «Yellow Cheddar»',
        '60 гр.',
        'TORTILA/04641_tortilla-chips_mat_yellow-cheddar_60gr-1-768x768.jpg',
    ),
    # HULIGAN
    (
        'huligan',
        'huligan-pretzel-crush-cheese-65',
        'Pretzel Crush «Cheese Sauce»',
        'Pretzel Crush «Cheese Sauce»',
        '65 гр.',
        'HULIGAN/huligan-pretzel-crush-cheese-sauce-pretzel-pieces-18x65g-5712-p.png',
    ),
    (
        'huligan',
        'huligan-pretzel-crush-honey-mustard-65',
        'Pretzel Crush «Honey Mustard Sauce»',
        'Pretzel Crush «Honey Mustard Sauce»',
        '65 гр.',
        'HULIGAN/huligan-pretzel-crush-honey-mustard-sauce_65g.png',
    ),
    (
        'huligan',
        'huligan-pretzel-crush-jalapeno-65',
        'Pretzel Crush «Jalapeno Sauce»',
        'Pretzel Crush «Jalapeno Sauce»',
        '65 гр.',
        'HULIGAN/huligan-pretzel-crush-jalapeno-sauce-pretzel-pieces-18x65g-5973-p.png',
    ),
    (
        'huligan',
        'huligan-pretzel-crush-siracha-65',
        'Pretzel Crush «Siracha Chilli Sauce»',
        'Pretzel Crush «Siracha Chilli Sauce»',
        '65 гр.',
        'HULIGAN/huligan-pretzel-crush-siracha-chilli-sauce-pretzel-pieces-18x65g-5710-p.png',
    ),
    # KRAMBALS (hashed filenames in zip)
    (
        'krambals',
        'krambals-bruschetta-tomato-mozzarella',
        'Брускетта «Tomato & Mozzarella»',
        'Bruschetta «Tomato & Mozzarella»',
        '70 гр.',
        'KRAMBALS/i62rda18x7o03z61308clgu5403u117o.png',
    ),
    (
        'krambals',
        'krambals-bruschetta-green-olives',
        'Брускетта «Green Olives & Sea Salt»',
        'Bruschetta «Green Olives & Sea Salt»',
        '70 гр.',
        'KRAMBALS/ojlzk22otalox6o55ute85rds22zzugh.png',
    ),
    (
        'krambals',
        'krambals-bruschetta-creamy-cheese',
        'Брускетта «Creamy Cheese»',
        'Bruschetta «Creamy Cheese»',
        '70 гр.',
        'KRAMBALS/qeh5sxrjqg4mgnjg6o8s0addw8xbau2l.png',
    ),
    (
        'krambals',
        'krambals-bruschetta-garden-grill',
        'Брускетта «Garden Grill»',
        'Bruschetta «Garden Grill»',
        '70 гр.',
        'KRAMBALS/u6xd0vzq1l6jdk8x1fkkkeakwqudaas6.png',
    ),
    (
        'krambals',
        'krambals-bruschetta-forest-mushrooms',
        'Брускетта «Forest Mushrooms & Butter»',
        'Bruschetta «Forest Mushrooms & Butter»',
        '70 гр.',
        'KRAMBALS/yqz4bl0ep5e1mj5ed5q42xfvfda7wtzs.png',
    ),
]


def _fix_zip_name(name: str) -> str:
    try:
        return name.encode('cp437').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return name


class Command(BaseCommand):
    help = 'Remove tea; add chips category and products from Чипсы.zip'

    def add_arguments(self, parser):
        parser.add_argument(
            '--zip',
            type=str,
            default=str(DEFAULT_ZIP),
            help='Path to Чипсы.zip',
        )
        parser.add_argument(
            '--force-images',
            action='store_true',
            help='Overwrite product images even if already set',
        )

    def handle(self, *args, **options):
        zip_path = Path(options['zip'])
        if not zip_path.is_file():
            raise CommandError(f'Zip not found: {zip_path}')

        with zipfile.ZipFile(zip_path) as zf:
            members = {_fix_zip_name(i.filename): i for i in zf.infolist()}
            with transaction.atomic():
                removed = self._remove_tea()
                chips_cat = self._ensure_chips_category()
                created, updated = self._ensure_chips(
                    zf, members, chips_cat, force_images=options['force_images']
                )

        invalidate_catalog_list_cache()
        self.stdout.write(
            self.style.SUCCESS(
                f'Done. tea_removed={removed}, chips_created={created}, '
                f'chips_updated={updated}'
            )
        )

    def _remove_tea(self) -> int:
        tea = Category.objects.filter(slug='tea').first()
        removed = 0
        if tea:
            removed = Product.objects.filter(category=tea).count()
            Product.objects.filter(category=tea).delete()
            tea.delete()
            self.stdout.write(f'Removed tea category and {removed} product(s)')

        brand = Brand.objects.filter(slug='prince-of-chester').first()
        if brand and brand.is_active:
            brand.is_active = False
            brand.save(update_fields=['is_active', 'updated_at'])
            self.stdout.write('Deactivated brand prince-of-chester')

        # Orphan tea products without category (safety)
        orphan = Product.objects.filter(slug__startswith='prince-of-chester')
        if orphan.exists():
            n = orphan.count()
            orphan.delete()
            removed += n
            self.stdout.write(f'Removed {n} orphan Prince of Chester product(s)')

        return removed

    def _ensure_chips_category(self) -> Category:
        cat, created = Category.objects.get_or_create(
            slug='chips',
            defaults={
                'name': 'Чипсы',
                'name_ru': 'Чипсы',
                'name_uz': 'Chipslar',
                'name_en': 'Chips',
                'order': 4,
                'is_active': True,
            },
        )
        if not created:
            cat.name = 'Чипсы'
            cat.name_ru = 'Чипсы'
            cat.name_uz = 'Chipslar'
            cat.name_en = 'Chips'
            cat.order = 4
            cat.is_active = True
            cat.save()
        else:
            self.stdout.write('Created category chips')
        return cat

    def _ensure_chips(
        self,
        zf: zipfile.ZipFile,
        members: dict,
        category: Category,
        *,
        force_images: bool,
    ) -> tuple[int, int]:
        brands = {
            b.slug: b
            for b in Brand.objects.filter(
                slug__in={'riceup', 'huligan', 'krambals'}
            )
        }
        missing = {'riceup', 'huligan', 'krambals'} - set(brands)
        if missing:
            raise CommandError(f'Missing brands in DB: {sorted(missing)}')

        created = updated = 0
        for order, (
            brand_slug,
            slug,
            name_ru,
            name_en,
            package,
            member_suffix,
        ) in enumerate(CHIPS_PRODUCTS):
            member_key = self._find_member(members, member_suffix)
            if not member_key:
                raise CommandError(f'Missing image in zip: {member_suffix}')

            brand = brands[brand_slug]
            product, was_created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'brand': brand,
                    'category': category,
                    'name': name_ru,
                    'name_ru': name_ru,
                    'name_en': name_en,
                    'name_uz': name_ru,
                    'package': package,
                    'package_ru': package,
                    'package_en': package,
                    'package_uz': package,
                    'order': order,
                    'is_active': True,
                },
            )
            if was_created:
                created += 1
            else:
                product.brand = brand
                product.category = category
                product.name = name_ru
                product.name_ru = name_ru
                product.name_en = name_en
                product.name_uz = name_ru
                product.package = package
                product.package_ru = package
                product.package_en = package
                product.package_uz = package
                product.order = order
                product.is_active = True
                updated += 1

            if force_images or not product.image:
                raw = zf.read(members[member_key])
                ext = Path(member_suffix).suffix.lower() or '.png'
                filename = f'{slug}{ext}'
                product.image.save(filename, ContentFile(raw), save=False)

            product.save()
            self.stdout.write(
                f'  {"+" if was_created else "~"} {brand.name}: {product.name}'
            )

        return created, updated

    @staticmethod
    def _find_member(members: dict, suffix: str) -> str | None:
        for key in members:
            if key.endswith(suffix) or key.replace('\\', '/').endswith(suffix):
                if not key.endswith('/'):
                    return key
        return None
