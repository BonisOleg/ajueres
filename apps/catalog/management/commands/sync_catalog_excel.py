"""Повна синхронізація каталогу з Excel + zip фото товарів."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image

from apps.catalog.models import Brand, Category, Product
from apps.catalog.selectors import invalidate_catalog_list_cache
from apps.core.import_content_data import BRANDS_SPEC, CATEGORIES, PRODUCT_IMAGES_DIR
from apps.core.models import SiteBlock
from apps.core.selectors import invalidate_site_blocks_cache

ROOT = Path(__file__).resolve().parents[4]
CATALOG_JSON = ROOT / 'content' / 'catalog_products.json'
STATIC_CATALOG = ROOT / 'static' / 'img' / 'catalog'
CANVAS = 1000
OBJECT_LIMIT = 920

DEFAULT_XLSX = Path.home() / 'Downloads' / 'Перевод_названий (2).xlsx'
DEFAULT_ZIP = Path.home() / 'Downloads' / 'Фото_Товара_Все.zip'
RICE_PAPER_ORIG = (
    Path.home() / 'Downloads' / 'SENSOY Фото' / 'Sen Soy' / '4607041133771.jpg'
)

BRAND_ALIASES = {
    'sen soy': 'sen-soy',
    'ямчан': 'yamchan',
    'папричи': 'paprichi',
    'riceup': 'riceup',
    'krambals': 'krambals',
    'huligan': 'huligan',
}

# Стабільні slug для вже існуючих снеків (щоб не плодити дублі).
KNOWN_SLUGS = {
    44: 'riceup-rice-chips-barbecue-60',
    45: 'riceup-rice-chips-cheese-60',
    46: 'riceup-rice-chips-hot-chili-60',
    47: 'riceup-rice-chips-ketchup-60',
    48: 'riceup-rice-chips-sea-salt-60',
    49: 'riceup-rice-chips-sour-cream-onion-60',
    50: 'riceup-tortilla-black-olives-60',
    51: 'riceup-tortilla-nacho-cheese-60',
    52: 'riceup-tortilla-salt-60',
    53: 'riceup-tortilla-sour-cream-onion-60',
    54: 'riceup-tortilla-texas-bbq-60',
    55: 'riceup-tortilla-yellow-cheddar-60',
    56: 'krambals-bruschetta-tomato-mozzarella',
    57: 'krambals-bruschetta-green-olives',
    58: 'krambals-bruschetta-creamy-cheese',
    59: 'krambals-bruschetta-garden-grill',
    60: 'krambals-bruschetta-forest-mushrooms',
    61: 'huligan-pretzel-crush-cheese-65',
    62: 'huligan-pretzel-crush-honey-mustard-65',
    63: 'huligan-pretzel-crush-jalapeno-65',
    64: 'huligan-pretzel-crush-siracha-65',
}

_SLUG_RE = re.compile(r'[^a-z0-9]+')


def _slugify(text: str) -> str:
    text = (
        str(text)
        .lower()
        .replace('«', '')
        .replace('»', '')
        .replace('“', '')
        .replace('”', '')
        .replace('"', '')
        .replace("'", '')
        .replace('&', ' and ')
    )
    text = _SLUG_RE.sub('-', text).strip('-')
    return text[:72] or 'product'


def _brand_slug(raw: str) -> str:
    key = (raw or '').strip().lower()
    if key not in BRAND_ALIASES:
        raise CommandError(f'Unknown brand in Excel: {raw!r}')
    return BRAND_ALIASES[key]


def _infer_category(name_ru: str) -> str:
    n = (name_ru or '').lower()
    if 'рисова бумага' in n or 'рисовая бумага' in n:
        return 'rice-paper'
    if 'брускетт' in n:
        return 'bruschetta'
    if 'прецель' in n or 'краш' in n:
        return 'crush'
    if 'чипсы' in n or 'тортилья' in n:
        return 'chips'
    if 'суши нори' in n:
        return 'seaweed'
    if 'лапша' in n:
        return 'noodles'
    return 'sauces'


def _format_package(weight) -> tuple[str, str, str]:
    if weight is None or weight == '':
        return '', '', ''
    value = float(weight)
    if value >= 1000:
        ru = '1 л.'
        en = '1 L'
        uz = '1 l'
    elif value == int(value):
        n = int(value)
        ru = f'{n} гр.'
        en = f'{n} g'
        uz = f'{n} g'
    else:
        s = str(weight).replace('.', ',')
        ru = f'{s} гр.'
        en = f'{weight} g'
        uz = f'{weight} g'
    return ru, en, uz


def _make_slug(num: int, brand: str, name_en: str, name_ru: str, weight) -> str:
    if num in KNOWN_SLUGS:
        return KNOWN_SLUGS[num]
    base = _slugify(name_en) or _slugify(name_ru)
    w = ''
    if weight is not None and weight != '':
        wv = float(weight)
        w = f'-{int(wv)}' if wv == int(wv) else f'-{str(weight).replace(".", "")}'
        if wv >= 1000:
            w = '-1l'
    # Excel № у slug гарантує унікальність при однакових EN-назвах.
    return f'{brand}-{base}{w}-{num}'[:120]


def _on_white(image: Image.Image) -> Image.Image:
    """Повний кадр на білому квадраті — без вирізання фону."""
    rgba = image.convert('RGBA')
    scale = min(OBJECT_LIMIT / rgba.width, OBJECT_LIMIT / rgba.height, 1.0)
    size = (max(1, round(rgba.width * scale)), max(1, round(rgba.height * scale)))
    if size != rgba.size:
        rgba = rgba.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (CANVAS, CANVAS), (255, 255, 255, 255))
    offset = ((CANVAS - size[0]) // 2, (CANVAS - size[1]) // 2)
    canvas.alpha_composite(rgba, offset)
    return canvas.convert('RGB')


def _find_photo(extract_dir: Path, num: int) -> Path:
    for ext in ('.png', '.jpg', '.jpeg', '.webp', '.PNG', '.JPG', '.JPEG', '.WEBP'):
        path = extract_dir / f'{num}{ext}'
        if path.is_file():
            return path
    raise CommandError(f'Photo not found for product №{num}')


def _static_name(brand: str, payload: bytes, ext: str = '.png') -> str:
    digest = hashlib.md5(payload).hexdigest()[:10]
    return f'{brand}-{digest}{ext}'


class Command(BaseCommand):
    help = 'Sync catalog products from Excel translations + product photo zip'

    def add_arguments(self, parser):
        parser.add_argument('--xlsx', type=Path, default=DEFAULT_XLSX)
        parser.add_argument('--zip', type=Path, default=DEFAULT_ZIP)
        parser.add_argument(
            '--skip-seed-blocks',
            action='store_true',
            help='Do not refresh CMS blocks via seed_site',
        )

    def handle(self, *args, **options):
        xlsx: Path = options['xlsx'].expanduser().resolve()
        zip_path: Path = options['zip'].expanduser().resolve()
        if not xlsx.is_file():
            raise CommandError(f'Excel not found: {xlsx}')
        if not zip_path.is_file():
            raise CommandError(f'Zip not found: {zip_path}')

        try:
            import openpyxl
        except ImportError as exc:
            raise CommandError('openpyxl is required') from exc

        extract_dir = ROOT / '.tmp' / 'catalog_photos'
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)

        wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
        ws = wb.active
        rows_out: list[dict] = []
        keep_slugs: set[str] = set()

        PRODUCT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        STATIC_CATALOG.mkdir(parents=True, exist_ok=True)

        self._ensure_categories_brands()

        with transaction.atomic():
            for cells in ws.iter_rows(min_row=2, values_only=True):
                num, name_ru, name_en, name_uz, weight, brand_raw = cells[:6]
                if num is None or not name_ru:
                    continue
                num = int(num)
                brand = _brand_slug(str(brand_raw))
                category = _infer_category(str(name_ru))
                slug = _make_slug(
                    num, brand, str(name_en or name_ru), str(name_ru), weight
                )
                package, package_en, package_uz = _format_package(weight)

                photo = _find_photo(extract_dir, num)
                # Рисова бумага — оригінал SENSOY на білому (без вирізання).
                if num == 18 and RICE_PAPER_ORIG.is_file():
                    photo = RICE_PAPER_ORIG

                image = _on_white(Image.open(photo))
                content_name = f'{slug}.png'
                content_path = PRODUCT_IMAGES_DIR / content_name
                image.save(content_path, 'PNG', optimize=True)
                payload = content_path.read_bytes()
                static_name = _static_name(brand, payload, '.png')
                (STATIC_CATALOG / static_name).write_bytes(payload)

                row = {
                    'slug': slug,
                    'name': str(name_ru).strip(),
                    'name_en': str(name_en or '').strip(),
                    'name_uz': str(name_uz or '').strip(),
                    'package': package,
                    'package_en': package_en,
                    'package_uz': package_uz,
                    'brand': brand,
                    'category': category,
                    'order': num - 1,
                    'image': content_name,
                    'static_image': static_name,
                }
                rows_out.append(row)
                keep_slugs.add(slug)
                self._upsert_product(row, content_path)

            Product.objects.exclude(slug__in=keep_slugs).update(is_active=False)

        CATALOG_JSON.write_text(
            json.dumps(rows_out, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )

        SiteBlock.objects.update_or_create(
            page='home',
            key='brands_title',
            defaults={'text_html': 'Наши партнёры'},
        )
        SiteBlock.objects.update_or_create(
            page='home',
            key='brands_subtitle',
            defaults={
                'text_html': (
                    'Ритейл-партнёры и производители, с которыми мы развиваем '
                    'ассортимент на рынке Узбекистана'
                )
            },
        )
        invalidate_catalog_list_cache()
        invalidate_site_blocks_cache()

        if not options['skip_seed_blocks']:
            call_command('seed_site')

        self.stdout.write(
            self.style.SUCCESS(
                f'Synced {len(rows_out)} products; deactivated extras; '
                f'JSON → {CATALOG_JSON}'
            )
        )

    def _ensure_categories_brands(self):
        cat_map = {}
        for slug, name_ru, name_uz, name_en, order, parent_slug in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name_ru, 'order': order, 'is_active': True},
            )
            cat.name = name_ru
            cat.order = order
            cat.is_active = True
            for field, value in (
                ('name_ru', name_ru),
                ('name_uz', name_uz),
                ('name_en', name_en),
            ):
                if hasattr(cat, field):
                    setattr(cat, field, value)
            cat.save()
            cat_map[slug] = cat
        for slug, _ru, _uz, _en, order, parent_slug in CATEGORIES:
            cat = cat_map[slug]
            cat.parent = cat_map.get(parent_slug) if parent_slug else None
            cat.order = order
            cat.save(update_fields=['parent', 'order'])

        for slug, name, _logo, order, featured in BRANDS_SPEC:
            brand, _ = Brand.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'order': order,
                    'is_active': True,
                    'is_featured': featured,
                },
            )
            brand.name = name
            brand.order = order
            brand.is_featured = featured
            brand.is_active = True
            brand.save()

    def _upsert_product(self, row: dict, content_path: Path):
        brand = Brand.objects.get(slug=row['brand'])
        category = Category.objects.get(slug=row['category'])
        product, _ = Product.objects.get_or_create(
            slug=row['slug'],
            defaults={
                'brand': brand,
                'category': category,
                'name': row['name'],
                'package': row['package'],
                'order': row['order'],
                'is_active': True,
            },
        )
        product.brand = brand
        product.category = category
        product.name = row['name']
        product.package = row['package']
        product.order = row['order']
        product.is_active = True
        for field, value in (
            ('name_ru', row['name']),
            ('name_en', row.get('name_en') or ''),
            ('name_uz', row.get('name_uz') or ''),
            ('package_ru', row['package']),
            ('package_en', row.get('package_en') or row['package']),
            ('package_uz', row.get('package_uz') or row['package']),
        ):
            if hasattr(product, field):
                setattr(product, field, value)
        safe = f"{brand.slug}-{row['order']}.png"
        product.image.save(safe, ContentFile(content_path.read_bytes()), save=False)
        product.save()
