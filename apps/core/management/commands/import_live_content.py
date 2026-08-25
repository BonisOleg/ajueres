"""
Import live content from ajeres.uz catalog + RU/UZ copy decks.
Downloads product images and available brand logos.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.image_utils import replace_dark_background
from apps.catalog.models import Brand, Category, Product
from apps.catalog.selectors import invalidate_catalog_list_cache
from apps.core.import_content_data import (
    ABOUT_BLOCKS,
    ABOUT_SECTIONS,
    ADVANTAGE_ROWS,
    BRAND_I18N,
    BRAND_LOGOS_DIR,
    BRANDS_SPEC,
    CATEGORIES,
    CONTACTS_BLOCKS,
    HOME_BLOCKS,
    INACTIVE_CATEGORY_SLUGS,
    NAME_FIX_BY_IMG,
    PARTNER_ROWS,
    RETAIL_LOGOS_DIR,
    RETAIL_PARTNERS_SPEC,
    STATIC_BRAND_LOGOS_DIR,
    STATIC_RETAIL_LOGOS_DIR,
    STAT_ROWS,
    resolve_logo_path,
)
from apps.core.models import (
    AboutSection,
    Advantage,
    CompanyStat,
    PartnerOffer,
    RetailPartner,
    SiteBlock,
    SiteSettings,
)
from apps.core.selectors import invalidate_retail_partners_cache, invalidate_site_blocks_cache

BASE = 'https://ajeres.uz'
UA = {'User-Agent': 'AJERES-Importer/1.0 (+local-dev)'}


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def abs_url(path: str) -> str:
    if path.startswith('http'):
        return path
    if not path.startswith('/'):
        path = '/' + path
    return BASE + path


def guess_category(name: str) -> str:
    n = name.lower()
    if any(x in n for x in ('рисова бумага', 'рисовая бумага', 'rice paper')):
        return 'rice-paper'
    if 'чипсы нори' in n or ('нори' in n and 'чип' in n):
        return 'chips'
    if any(x in n for x in ('суши нори', 'нори', 'nori')):
        return 'seaweed'
    if any(x in n for x in ('брускетт', 'bruschetta')):
        return 'bruschetta'
    if any(x in n for x in ('crush', 'pretzel', 'краш')):
        return 'crush'
    if any(x in n for x in ('чипсы', 'chips', 'tortilla', 'тортиль', 'рисовые чипсы')):
        return 'chips'
    if any(
        x in n
        for x in (
            'лапша',
            'somen',
            'udon',
            'noodle',
            'vermicelli',
            'fo - kho',
            'fo-kho',
        )
    ):
        return 'noodles'
    return 'sauces'


def clean_product_name(raw: str, brand_name: str) -> str:
    name = re.sub(r'\s+', ' ', raw).strip()
    for prefix in (brand_name, 'Sen Soy', 'Prince of Chester', 'Чай Prince of Chester'):
        if name.lower().startswith(prefix.lower()):
            name = name[len(prefix) :].strip(' —-')
    name = re.sub(r'^Чай\s+', '', name).strip()
    return name or raw.strip()


class Command(BaseCommand):
    help = 'Import texts/images from ajeres.uz + RU/UZ documents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-texts',
            action='store_true',
            help='Overwrite existing CMS/list texts',
        )

    def handle(self, *args, **options):
        force = options['force_texts']
        self.stdout.write('Downloading catalog…')
        html = fetch_bytes(f'{BASE}/catalog.html').decode('utf-8', errors='ignore')
        products = self._parse_catalog(html)
        self.stdout.write(f'Parsed {len(products)} products')

        self._settings(force)
        self._categories(force)
        self._content_texts(force)
        brands = self._brands_and_logos(force)
        self._retail_partners()
        self._import_products(products, brands)
        self._hero_image(force)
        invalidate_catalog_list_cache()
        invalidate_site_blocks_cache()
        invalidate_retail_partners_cache()
        self.stdout.write(self.style.SUCCESS('Import finished'))

    def _parse_catalog(self, html: str) -> list[dict]:
        items: list[dict] = []
        parts = re.split(r'<p class="subheading">', html)
        for part in parts[1:]:
            bm = re.match(r'([^<]+)</p>', part)
            section = (bm.group(1).strip() if bm else 'SenSoy').lower()
            brand_key = 'sen-soy' if 'sen' in section else 'prince-of-chester'
            for block in re.finditer(r'<div role="listitem"[\s\S]*?</a>\s*</div>', part):
                b = block.group(0)
                name_m = re.search(r'product-name">([^<]+)', b)
                pkg_m = re.search(r'f_price_[\s\S]*?>([^<]+)</div>', b)
                srcset = re.search(r'srcset="([^"]+)"', b)
                src_m = re.search(r'src="((?:/products/|https://)[^"]+)"', b)
                img = ''
                if srcset and srcset.group(1).startswith('/'):
                    img = srcset.group(1).split()[0]
                elif src_m:
                    img = src_m.group(1)
                    if 'cdn.prod.website-files' in img and srcset:
                        local = srcset.group(1).split()[0]
                        if local.startswith('/'):
                            img = local
                raw_name = (name_m.group(1) if name_m else '').strip()
                fname = Path(img).name if img else ''
                if fname in NAME_FIX_BY_IMG:
                    raw_name = NAME_FIX_BY_IMG[fname]
                items.append(
                    {
                        'brand_key': brand_key,
                        'raw_name': raw_name,
                        'package': (pkg_m.group(1) if pkg_m else '').strip(),
                        'img': img,
                    }
                )
        return items

    def _save_image_bytes(self, field, filename: str, data: bytes) -> bool:
        processed = replace_dark_background(data)
        if not filename.lower().endswith('.png'):
            filename = f'{Path(filename).stem}.png'
        field.save(filename, ContentFile(processed), save=False)
        return True

    def _save_raw_image_bytes(self, field, filename: str, data: bytes) -> bool:
        field.save(filename, ContentFile(data), save=False)
        return True

    def _assign_file(self, field, url: str, filename: str) -> bool:
        try:
            data = fetch_bytes(abs_url(url) if not url.startswith('http') else url)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            self.stderr.write(f'  skip image {url}: {exc}')
            return False
        return self._save_image_bytes(field, filename, data)

    def _assign_local(self, field, path: Path, filename: str | None = None) -> bool:
        if not path.is_file():
            self.stderr.write(f'  skip local image {path}')
            return False
        return self._save_image_bytes(field, filename or path.name, path.read_bytes())

    def _assign_file_raw(self, field, url: str, filename: str) -> bool:
        try:
            data = fetch_bytes(abs_url(url) if not url.startswith('http') else url)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            self.stderr.write(f'  skip image {url}: {exc}')
            return False
        return self._save_raw_image_bytes(field, filename, data)

    def _settings(self, force: bool):
        s = SiteSettings.load()
        s.phone = '+(998) 93-541-88-86'
        s.email = 'info@ajeres.uz'
        if force or not s.company_name:
            s.company_name = 'AJERES'
            s.company_name_ru = 'AJERES'
            s.company_name_uz = 'AJERES'
            s.company_name_en = 'AJERES'
        s.address = (
            'Ташкент, Мирзо-Улугбекский район, ул. Паркентская 327'
        )
        s.address_ru = s.address
        s.address_uz = (
            'Toshkent shahri, Mirzo Ulug‘bek tumani, Parkent ko‘chasi, 327'
        )
        s.address_en = (
            'Tashkent, Mirzo Ulugbek district, Parkentskaya st. 327'
        )
        s.save()

    def _categories(self, force: bool):
        by_slug: dict[str, Category] = {}
        for slug, ru, uz, en, order, parent_slug in CATEGORIES:
            cat, _ = Category.objects.get_or_create(slug=slug)
            by_slug[slug] = cat
            if force or not cat.name_ru:
                cat.name = ru
                cat.name_ru = ru
                cat.name_uz = uz
                cat.name_en = en
            cat.order = order
            cat.is_active = True
            cat.save()

        for slug, _ru, _uz, _en, order, parent_slug in CATEGORIES:
            cat = by_slug[slug]
            cat.parent = by_slug.get(parent_slug) if parent_slug else None
            cat.order = order
            cat.save(update_fields=['parent', 'order', 'updated_at'])

        if INACTIVE_CATEGORY_SLUGS:
            Category.objects.filter(slug__in=INACTIVE_CATEGORY_SLUGS).update(
                is_active=False
            )

    def _set_block(self, page, key, text, force):
        obj, created = SiteBlock.objects.get_or_create(
            page=page, key=key, defaults={'text_html': text}
        )
        if created or force:
            obj.text_html = text
            obj.save()

    def _content_texts(self, force: bool):
        for key, text in HOME_BLOCKS.items():
            self._set_block('home', key, text, force)
        for key, text in ABOUT_BLOCKS.items():
            self._set_block('about', key, text, force)
        for key, text in CONTACTS_BLOCKS.items():
            self._set_block('contacts', key, text, force)

        if force:
            Advantage.objects.all().delete()
        if not Advantage.objects.exists():
            for i, row in enumerate(ADVANTAGE_ROWS):
                Advantage.objects.create(
                    icon_key=row[0],
                    title=row[1],
                    title_ru=row[1],
                    title_uz=row[3],
                    title_en=row[5],
                    text=row[2],
                    text_ru=row[2],
                    text_uz=row[4],
                    text_en=row[6],
                    order=i,
                    is_active=True,
                )

        if force:
            CompanyStat.objects.all().delete()
        if not CompanyStat.objects.exists():
            for i, (v, ru, uz, en) in enumerate(STAT_ROWS):
                CompanyStat.objects.create(
                    value=v,
                    label=ru,
                    label_ru=ru,
                    label_uz=uz,
                    label_en=en,
                    order=i,
                    is_active=True,
                )

        if force:
            AboutSection.objects.all().delete()
        for i, row in enumerate(ABOUT_SECTIONS):
            obj, created = AboutSection.objects.get_or_create(
                section_key=row[0],
                defaults={'title': row[1], 'body': row[4], 'order': i},
            )
            if created or force:
                obj.title = row[1]
                obj.title_ru = row[1]
                obj.title_uz = row[2]
                obj.title_en = row[3]
                obj.body = row[4]
                obj.body_ru = row[4]
                obj.body_uz = row[5]
                obj.body_en = row[6]
                obj.order = i
                obj.is_active = True
                obj.save()

        if force:
            PartnerOffer.objects.all().delete()
        keep_ids = []
        for i, row in enumerate(PARTNER_ROWS):
            title_ru, title_uz, title_en, text_ru, text_uz, text_en = row
            offer = PartnerOffer.objects.filter(order=i).first()
            if offer is None or force:
                if offer is None:
                    offer = PartnerOffer(order=i)
            offer.title = title_ru
            offer.title_ru = title_ru
            offer.title_uz = title_uz
            offer.title_en = title_en
            offer.text = text_ru
            offer.text_ru = text_ru
            offer.text_uz = text_uz
            offer.text_en = text_en
            offer.order = i
            offer.is_active = True
            offer.save()
            keep_ids.append(offer.pk)
        PartnerOffer.objects.exclude(pk__in=keep_ids).update(is_active=False)

        from apps.core.legal_defaults import (
            OFFER_DEFAULTS,
            PRIVACY_DEFAULTS,
            ensure_legal_document,
        )

        ensure_legal_document('privacy', PRIVACY_DEFAULTS)
        ensure_legal_document('offer', OFFER_DEFAULTS)

    def _brands_and_logos(self, force: bool) -> dict[str, Brand]:
        result = {}
        for slug, name, logo_file, order, featured in BRANDS_SPEC:
            brand, _ = Brand.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'order': order, 'is_featured': featured},
            )
            brand.name = name
            name_ru, name_uz, name_en = BRAND_I18N.get(slug, (name, name, name))
            brand.name = name_ru
            if hasattr(brand, 'name_ru'):
                brand.name_ru = name_ru
                brand.name_uz = name_uz
                brand.name_en = name_en
            brand.order = order
            brand.is_featured = featured
            brand.is_active = True
            brand.short_description_ru = f'Бренд {name_ru} в портфеле AJERES'
            brand.short_description_uz = f'AJERES portfelidagi {name_uz} brendi'
            brand.short_description_en = f'{name_en} brand in the AJERES portfolio'
            if logo_file:
                local = resolve_logo_path(
                    logo_file, BRAND_LOGOS_DIR, STATIC_BRAND_LOGOS_DIR
                )
                if local is not None:
                    ok = self._assign_local(brand.logo, local, logo_file)
                    if ok:
                        self.stdout.write(f'  logo {name}')
                else:
                    self.stderr.write(f'  missing logo file {logo_file}')
            brand.save()
            result[slug] = brand
        return result

    def _retail_partners(self):
        for slug, name, logo_file, order in RETAIL_PARTNERS_SPEC:
            partner, _ = RetailPartner.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'order': order, 'is_active': True},
            )
            partner.name = name
            partner.name_ru = name
            partner.order = order
            partner.is_active = True
            local = resolve_logo_path(
                logo_file, RETAIL_LOGOS_DIR, STATIC_RETAIL_LOGOS_DIR
            )
            if local is not None:
                ok = self._assign_local(partner.logo, local, logo_file)
                if ok:
                    self.stdout.write(f'  retail logo {name}')
            else:
                self.stderr.write(f'  missing retail logo {logo_file}')
            partner.save()

    def _import_products(self, products: list[dict], brands: dict[str, Brand]):
        cats = {c.slug: c for c in Category.objects.all()}
        Product.objects.all().delete()
        for i, item in enumerate(products):
            brand = brands[item['brand_key']]
            raw = item['raw_name']
            name = clean_product_name(raw, brand.name)
            package = item['package'] or ''
            cat_slug = guess_category(raw)
            category = cats[cat_slug]
            base_slug = slugify(f'{brand.slug}-{name}-{package}', allow_unicode=True)
            slug = base_slug[:120] or f'product-{i}'
            original = slug
            n = 2
            while Product.objects.filter(slug=slug).exists():
                slug = f'{original}-{n}'
                n += 1
            product = Product(
                brand=brand,
                category=category,
                slug=slug,
                name=name,
                name_ru=name,
                name_uz=name,
                name_en=name,
                package=package,
                package_ru=package,
                package_uz=package,
                package_en=package,
                order=i,
                is_active=True,
            )
            if item['img']:
                fname = Path(item['img']).name
                self._assign_file_raw(product.image, item['img'], fname)
            product.save()
            self.stdout.write(f'  product {product}')

    def _hero_image(self, force: bool):
        """
        Canonical homepage hero is static/img/hero-samarkand.webp.
        Never fall back to product art (e.g. Sen Soy chili) — that used to
        override the Samarkand fallback in templates via CMS hero_image.
        """
        block, _ = SiteBlock.objects.get_or_create(
            page='home', key='hero_image', defaults={'text_html': ''}
        )
        static_root = Path(__file__).resolve().parents[4] / 'static' / 'img'
        candidates = (
            static_root / 'hero-samarkand.webp',
            static_root / 'hero-samarkand.png',
        )
        local = next((p for p in candidates if p.is_file()), None)
        if local is None:
            self.stderr.write(
                '  skip hero: static/img/hero-samarkand.webp missing'
            )
            return

        current = (block.image.name or '').lower() if block.image else ''
        is_wrong = any(
            bad in current
            for bad in ('chill', 'hero-illustration', 'sensoy', 'hero-chill')
        )
        if force or not block.image or is_wrong:
            ok = self._save_raw_image_bytes(
                block.image, 'hero-samarkand.webp', local.read_bytes()
            )
            if ok:
                block.save()
                invalidate_site_blocks_cache()
                self.stdout.write(f'  hero image set from {local.name}')
