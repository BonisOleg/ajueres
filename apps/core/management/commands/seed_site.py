"""Idempotent seed: settings, CMS blocks, categories, brands, sample products."""

import json
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Brand, Category, Product
from apps.catalog.selectors import invalidate_catalog_list_cache
from apps.core.import_content_data import (
    ABOUT_SECTIONS,
    ADVANTAGE_ROWS,
    BRAND_I18N,
    BRAND_LOGOS_DIR,
    BRANDS_SPEC,
    CATEGORIES,
    INACTIVE_CATEGORY_SLUGS,
    PARTNER_ROWS,
    PRODUCT_IMAGES_DIR,
    RETAIL_LOGOS_DIR,
    RETAIL_PARTNERS_SPEC,
    STAT_ROWS,
)
from apps.core.models import (
    AboutSection,
    Advantage,
    CompanyStat,
    LegalDocument,
    PartnerOffer,
    RetailPartner,
    SiteBlock,
    SiteSettings,
)
from apps.core.selectors import invalidate_retail_partners_cache, invalidate_site_blocks_cache

# Minimal 1x1 PNG fallback only when no content file exists.
_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
    b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
    b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)

_CATALOG_JSON = Path(__file__).resolve().parents[4] / 'content' / 'catalog_products.json'


class Command(BaseCommand):
    help = 'Seed AJERES demo/content data (safe to re-run)'

    def handle(self, *args, **options):
        self._settings()
        self._blocks()
        self._advantages()
        self._stats()
        self._about()
        self._partners()
        self._retail_partners()
        self._privacy()
        self._catalog()
        invalidate_catalog_list_cache()
        invalidate_site_blocks_cache()
        invalidate_retail_partners_cache()
        self.stdout.write(self.style.SUCCESS('Seed complete'))

    def _settings(self):
        s = SiteSettings.load()
        s.company_name = s.company_name or 'AJERES'
        s.phone = s.phone or '+(998) 93-541-88-86'
        s.email = s.email or 'info@ajeres.uz'
        address = 'Ташкент, Мирзо-Улугбекский район, ул. Паркентская 327'
        s.address = address
        for field, value in (
            ('address_ru', address),
            (
                'address_uz',
                'Toshkent shahri, Mirzo Ulug‘bek tumani, Parkent ko‘chasi, 327',
            ),
            (
                'address_en',
                'Tashkent, Mirzo Ulugbek district, Parkentskaya st. 327',
            ),
        ):
            if hasattr(s, field):
                setattr(s, field, value)
        s.save()
        from apps.core.models import BlockStyle, SiteButtonStyle

        SiteButtonStyle.ensure_defaults()
        BlockStyle.ensure_defaults()

    def _set_block(self, page, key, text='', image=None):
        obj, created = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults={'text_html': text},
        )
        if created:
            return
        if text and obj.text_html != text:
            obj.text_html = text
            obj.save()

    def _blocks(self):
        pairs = [
            ('home', 'hero_visible', '1'),
            ('home', 'advantages_visible', '1'),
            ('home', 'brands_visible', '1'),
            ('home', 'cases_visible', '0'),
            ('home', 'hero_eyebrow', 'Дистрибьютор с 2018 года'),
            (
                'home',
                'hero_title',
                'Лучшие бренды в своем сегменте на рынке Узбекистана',
            ),
            (
                'home',
                'hero_text',
                'Импорт, эксклюзивная дистрибуция, вывод на рынок Узбекистана '
                'новых производителей.',
            ),
            ('home', 'hero_cta', 'Связаться с нами'),
            ('home', 'services_title', 'Наша деятельность'),
            ('home', 'brands_title', 'Наши партнёры'),
            (
                'home',
                'brands_subtitle',
                'Ритейл-партнёры и производители, с которыми мы развиваем '
                'ассортимент на рынке Узбекистана',
            ),
            ('home', 'coop_title', 'Сотрудничество'),
            ('home', 'coop_eyebrow', 'Для торговых сетей, дистрибьюторов и HoReCa'),
            ('home', 'coop_cta', 'Стать партнером'),
            ('home', 'cta_title', 'Начнём сотрудничество?'),
            (
                'home',
                'cta_text',
                'Свяжитесь с нами в любое удобное время, профессиональная команда '
                'специалистов готова ответить на все вопросы и обсудить '
                'взаимовыгодное сотрудничество',
            ),
            ('about', 'eyebrow', 'О компании'),
            ('about', 'title', 'ООО «AJERES»'),
            (
                'about',
                'intro',
                'Современная дистрибьюторская компания на рынке продуктов '
                'питания Республики Узбекистан. Специализируемся на выводе '
                'международных брендов и полном комплексе услуг: импорт, '
                'логистика, продажи, маркетинг и развитие брендов.',
            ),
            ('about', 'cta', 'Связаться с нами'),
            ('about', 'side_image', ''),
            ('contacts', 'eyebrow', 'Контакты'),
            ('contacts', 'title', 'Свяжитесь с нами'),
            (
                'contacts',
                'intro',
                'Команда ООО «AJERES» всегда открыта для новых партнерств и '
                'готова обсудить возможности сотрудничества.\n\n'
                'Если вы являетесь производителем продуктов питания, '
                'представителем торговой сети или заинтересованы в развитии '
                'вашего бренда на рынке Узбекистана, свяжитесь с нами.\n\n'
                'Мы ответим на все вопросы, подготовим коммерческое предложение '
                'и предложим оптимальную стратегию выхода на рынок.',
            ),
            ('contacts', 'partners_title', 'Сотрудничество'),
            ('contacts', 'form_title', 'Отправить нам запрос'),
            (
                'contacts',
                'form_lead',
                'Команда ООО «AJERES» всегда открыта для новых партнерств и '
                'готова обсудить возможности сотрудничества.\n\n'
                'Если вы являетесь производителем продуктов питания, '
                'представителем торговой сети или заинтересованы в развитии '
                'вашего бренда на рынке Узбекистана, свяжитесь с нами.\n\n'
                'Мы ответим на все вопросы, подготовим коммерческое предложение '
                'и предложим оптимальную стратегию выхода на рынок.',
            ),
            ('contacts', 'phone_note', 'Пн–Сб, 9:00–18:00'),
            ('contacts', 'email_note', 'Отвечаем в течение дня'),
            ('contacts', 'wholesale_title', 'Оптовые поставки'),
            (
                'contacts',
                'wholesale_text',
                'Отгрузка со склада в Ташкенте и доставка по региону.',
            ),
            ('contacts', 'map_title', 'Наш офис в Ташкенте'),
        ]
        for page, key, text in pairs:
            self._set_block(page, key, text)

    def _advantages(self):
        keep_keys = set()
        for i, row in enumerate(ADVANTAGE_ROWS):
            icon, title_ru, text_ru, title_uz, text_uz, title_en, text_en = row
            keep_keys.add(icon)
            obj, _ = Advantage.objects.get_or_create(
                icon_key=icon,
                defaults={
                    'title': title_ru,
                    'text': text_ru,
                    'order': i,
                    'is_active': True,
                },
            )
            obj.title = title_ru
            obj.text = text_ru
            obj.order = i
            obj.is_active = True
            update_fields = ['title', 'text', 'order', 'is_active']
            for field, value in (
                ('title_ru', title_ru),
                ('text_ru', text_ru),
                ('title_uz', title_uz),
                ('text_uz', text_uz),
                ('title_en', title_en),
                ('text_en', text_en),
            ):
                if hasattr(obj, field):
                    setattr(obj, field, value)
                    update_fields.append(field)
            obj.save(update_fields=list(dict.fromkeys(update_fields)))
        Advantage.objects.exclude(icon_key__in=keep_keys).update(is_active=False)

    def _stats(self):
        keep_values = set()
        for order, (value, label_ru, label_uz, label_en) in enumerate(STAT_ROWS):
            keep_values.add(value)
            obj, _ = CompanyStat.objects.get_or_create(
                value=value,
                defaults={
                    'label': label_ru,
                    'order': order,
                    'is_active': True,
                },
            )
            obj.label = label_ru
            obj.order = order
            obj.is_active = True
            update_fields = ['label', 'order', 'is_active']
            for field, text in (
                ('label_ru', label_ru),
                ('label_uz', label_uz),
                ('label_en', label_en),
            ):
                if hasattr(obj, field):
                    setattr(obj, field, text)
                    update_fields.append(field)
            obj.save(update_fields=list(dict.fromkeys(update_fields)))
        CompanyStat.objects.exclude(value__in=keep_values).update(is_active=False)


    def _about(self):
        keep_keys = set()
        for i, row in enumerate(ABOUT_SECTIONS):
            key = row[0]
            keep_keys.add(key)
            title_ru, title_uz, title_en = row[1], row[2], row[3]
            body_ru, body_uz, body_en = row[4], row[5], row[6]
            obj, _ = AboutSection.objects.get_or_create(
                section_key=key,
                defaults={
                    'title': title_ru,
                    'body': body_ru,
                    'order': i,
                    'is_active': True,
                },
            )
            obj.title = title_ru
            obj.body = body_ru
            obj.order = i
            obj.is_active = True
            update_fields = ['title', 'body', 'order', 'is_active']
            for field, value in (
                ('title_ru', title_ru),
                ('title_uz', title_uz),
                ('title_en', title_en),
                ('body_ru', body_ru),
                ('body_uz', body_uz),
                ('body_en', body_en),
            ):
                if hasattr(obj, field):
                    setattr(obj, field, value)
                    update_fields.append(field)
            obj.save(update_fields=list(dict.fromkeys(update_fields)))
        AboutSection.objects.exclude(section_key__in=keep_keys).update(
            is_active=False
        )

    def _partners(self):
        keep_ids = []
        for i, row in enumerate(PARTNER_ROWS):
            title_ru, title_uz, title_en, text_ru, text_uz, text_en = row
            offer = PartnerOffer.objects.filter(order=i).first()
            if offer is None:
                offer = PartnerOffer(order=i)
            offer.title = title_ru
            offer.text = text_ru
            offer.order = i
            offer.is_active = True
            for field, value in (
                ('title_ru', title_ru),
                ('title_uz', title_uz),
                ('title_en', title_en),
                ('text_ru', text_ru),
                ('text_uz', text_uz),
                ('text_en', text_en),
            ):
                if hasattr(offer, field):
                    setattr(offer, field, value)
            offer.save()
            keep_ids.append(offer.pk)
        PartnerOffer.objects.exclude(pk__in=keep_ids).update(is_active=False)

    def _retail_partners(self):
        for slug, name, logo_file, order in RETAIL_PARTNERS_SPEC:
            partner, _ = RetailPartner.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'order': order,
                    'is_active': True,
                },
            )
            partner.name = name
            partner.order = order
            partner.is_active = True
            path = RETAIL_LOGOS_DIR / logo_file
            if path.is_file():
                partner.logo.save(
                    logo_file, ContentFile(path.read_bytes()), save=False
                )
            partner.save()

    def _privacy(self):
        LegalDocument.objects.get_or_create(
            slug='privacy',
            defaults={
                'title': 'Политика приватности',
                'body': (
                    'ООО «AJERES» обрабатывает персональные данные, переданные '
                    'через форму обратной связи, исключительно для ответа на '
                    'обращение и организации сотрудничества.\n\n'
                    'Мы не передаём данные третьим лицам без законных оснований '
                    'и принимаем меры для защиты информации.'
                ),
            },
        )

    def _ensure_image(self, field_file, filename: str):
        if field_file and getattr(field_file, 'name', None):
            return
        field_file.save(filename, ContentFile(_PNG), save=False)

    def _product_image_path(self, slug: str, image_name: str | None = None) -> Path | None:
        if image_name:
            path = PRODUCT_IMAGES_DIR / image_name
            if path.is_file() and path.stat().st_size > 2000:
                return path
        for path in PRODUCT_IMAGES_DIR.glob(f'{slug}.*'):
            if path.is_file() and path.stat().st_size > 2000:
                return path
        return None

    def _ensure_product_image(
        self,
        product: Product,
        *,
        image_name: str | None = None,
        force: bool = False,
    ):
        path = self._product_image_path(product.slug, image_name)
        if path is None:
            return
        current_size = 0
        try:
            current = getattr(product.image, 'path', None)
            if current and Path(current).is_file():
                current_size = Path(current).stat().st_size
        except (OSError, ValueError):
            current_size = 0
        if force or not product.image or current_size < 2000:
            # ASCII-safe media filename for serverless FS.
            ext = path.suffix.lower() if path.suffix else '.png'
            if ext not in {'.png', '.jpg', '.jpeg', '.webp'}:
                ext = '.png'
            safe_name = f'{product.brand.slug}-{product.pk or product.slug[:24]}{ext}'
            safe_name = ''.join(
                ch if ch.isascii() and (ch.isalnum() or ch in '-_.') else '-'
                for ch in safe_name
            )
            product.image.save(safe_name, ContentFile(path.read_bytes()), save=False)

    def _ensure_brand_logo(self, brand: Brand, logo_file: str | None, force: bool = False):
        if not logo_file:
            return
        path = BRAND_LOGOS_DIR / logo_file
        if not path.is_file():
            if force or not brand.logo:
                self._ensure_image(brand.logo, f'{brand.slug}.png')
            return
        if force or not brand.logo:
            brand.logo.save(logo_file, ContentFile(path.read_bytes()), save=False)

    def _load_catalog_rows(self) -> list[dict]:
        if not _CATALOG_JSON.is_file():
            self.stderr.write(f'Catalog JSON missing: {_CATALOG_JSON}')
            return []
        try:
            rows = json.loads(_CATALOG_JSON.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            self.stderr.write(f'Catalog JSON read error: {exc}')
            return []
        return [row for row in rows if isinstance(row, dict) and row.get('slug')]

    def _catalog(self):
        cat_map = {}
        for slug, name_ru, _uz, _en, order, _parent in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name_ru, 'order': order, 'is_active': True},
            )
            cat.is_active = True
            cat.name = name_ru
            if hasattr(cat, 'name_ru'):
                cat.name_ru = name_ru
            cat.order = order
            cat.save()
            cat_map[slug] = cat

        for slug, name_ru, name_uz, name_en, order, parent_slug in CATEGORIES:
            cat = cat_map[slug]
            cat.parent = cat_map.get(parent_slug) if parent_slug else None
            cat.order = order
            cat.is_active = True
            cat.name = name_ru
            update_fields = ['parent', 'order', 'is_active', 'name']
            for field, value in (
                ('name_ru', name_ru),
                ('name_uz', name_uz),
                ('name_en', name_en),
            ):
                if hasattr(cat, field):
                    setattr(cat, field, value)
                    update_fields.append(field)
            cat.save(update_fields=list(dict.fromkeys(update_fields)))

        if INACTIVE_CATEGORY_SLUGS:
            Category.objects.filter(slug__in=INACTIVE_CATEGORY_SLUGS).update(
                is_active=False
            )

        brand_map = {}
        for slug, name, logo_file, order, featured in BRANDS_SPEC:
            brand, _ = Brand.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'order': order,
                    'is_active': True,
                    'is_featured': featured,
                },
            )
            name_ru, name_uz, name_en = BRAND_I18N.get(
                slug, (name, name, name)
            )
            brand.name = name_ru
            brand.order = order
            brand.is_featured = featured
            brand.is_active = True
            for field, value in (
                ('name_ru', name_ru),
                ('name_uz', name_uz),
                ('name_en', name_en),
            ):
                if hasattr(brand, field):
                    setattr(brand, field, value)
            self._ensure_brand_logo(brand, logo_file, force=False)
            brand.save()
            brand_map[slug] = brand

        rows = self._load_catalog_rows()
        keep_slugs: set[str] = set()
        for row in rows:
            slug = row['slug']
            brand = brand_map.get(row.get('brand') or '')
            category = cat_map.get(row.get('category') or '')
            if not brand or not category:
                self.stderr.write(f'Skip product {slug}: unknown brand/category')
                continue
            keep_slugs.add(slug)
            name_ru = row.get('name') or row.get('name_ru') or slug
            name_en = row.get('name_en') or ''
            name_uz = row.get('name_uz') or ''
            package = row.get('package') or ''
            try:
                product, created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'brand': brand,
                        'category': category,
                        'name': name_ru,
                        'package': package,
                        'order': int(row.get('order') or 0),
                        'is_active': True,
                    },
                )
                product.brand = brand
                product.category = category
                product.name = name_ru
                product.package = package
                product.order = int(row.get('order') or 0)
                product.is_active = True
                for field, value in (
                    ('name_ru', name_ru),
                    ('name_en', name_en),
                    ('name_uz', name_uz),
                    ('package_ru', package),
                    ('package_en', row.get('package_en') or package),
                    ('package_uz', row.get('package_uz') or package),
                ):
                    if value and hasattr(product, field):
                        setattr(product, field, value)
                # On Vercel UI serves static/img/catalog; skip heavy media copies.
                if not getattr(settings, 'IS_VERCEL', False):
                    self._ensure_product_image(
                        product,
                        image_name=row.get('image'),
                        force=bool(row.get('force_image')),
                    )
                product.save()
            except Exception as exc:  # noqa: BLE001 — keep seeding other rows
                self.stderr.write(f'Skip product {slug}: {exc}')

        if keep_slugs:
            Product.objects.exclude(slug__in=keep_slugs).update(is_active=False)
