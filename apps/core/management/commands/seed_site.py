"""Idempotent seed: settings, CMS blocks, categories, brands, sample products."""

import json
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Brand, Category, Product
from apps.catalog.selectors import invalidate_catalog_list_cache
from apps.core.import_content_data import (
    ADVANTAGE_ROWS,
    BRAND_LOGOS_DIR,
    BRANDS_SPEC,
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

    def _set_block(self, page, key, text='', image=None):
        obj, created = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults={'text_html': text},
        )
        if created:
            return
        # do not overwrite existing content

    def _blocks(self):
        pairs = [
            ('home', 'hero_visible', '1'),
            ('home', 'advantages_visible', '1'),
            ('home', 'brands_visible', '1'),
            ('home', 'cases_visible', '0'),
            ('home', 'hero_eyebrow', 'Дистрибьютор с 2018 года'),
            ('home', 'hero_title', 'Азиатские вкусы для вашего бизнеса'),
            (
                'home',
                'hero_text',
                'Соусы, маринады, лапша, нори, сиропы и чипсы — '
                'оптовые поставки для магазинов и HoReCa.',
            ),
            ('home', 'hero_cta', 'Связаться с нами'),
            ('home', 'brands_title', 'Наши бренды'),
            (
                'home',
                'brands_subtitle',
                'Работаем напрямую с производителями, которым доверяют профессионалы',
            ),
            ('about', 'eyebrow', 'О компании'),
            ('about', 'title', 'ООО «AJERES»'),
            (
                'about',
                'intro',
                'Современная дистрибьюторская компания на рынке продуктов '
                'питания Республики Узбекистан.',
            ),
            ('about', 'cta', 'Связаться с нами'),
            ('about', 'side_image', ''),
            ('contacts', 'eyebrow', 'Контакты'),
            ('contacts', 'title', 'Свяжитесь с нами'),
            (
                'contacts',
                'intro',
                'Ответим на вопросы, пришлём прайс и подберём ассортимент '
                'под ваш формат бизнеса. Работаем с магазинами, HoReCa и '
                'дистрибьюторами.',
            ),
            ('contacts', 'partners_title', 'Для партнёров'),
            ('contacts', 'form_title', 'Отправить нам запрос'),
            (
                'contacts',
                'form_lead',
                'Заполните форму — свяжемся с вами и пришлём предложение.',
            ),
            ('contacts', 'phone_note', 'Пн–Сб, 9:00–18:00'),
            ('contacts', 'email_note', 'Отвечаем в течение дня'),
            ('contacts', 'wholesale_title', 'Оптовые поставки'),
            (
                'contacts',
                'wholesale_text',
                'Отгрузка со склада в Ташкенте и доставка по региону.',
            ),
            ('contacts', 'map_title', 'Наш склад в Ташкенте'),
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
        if AboutSection.objects.exists():
            return
        sections = [
            (
                'history',
                'О компании',
                'ООО «AJERES» — современная дистрибьюторская компания, '
                'работающая на рынке продуктов питания Республики Узбекистан.\n\n'
                'Мы специализируемся на выводе международных брендов на местный '
                'рынок и обеспечиваем полный комплекс услуг: импорт, логистику, '
                'продажи, маркетинг и развитие брендов.',
            ),
            (
                'mission',
                'Наша миссия',
                'Предоставлять потребителям Узбекистана качественные продукты '
                'питания мирового уровня и помогать международным производителям '
                'успешно развивать свой бизнес в Центральной Азии.',
            ),
            (
                'vision',
                'Наше видение',
                'Стать одним из ведущих дистрибьюторов международных брендов '
                'продуктов питания в регионе.',
            ),
        ]
        for i, (key, title, body) in enumerate(sections):
            AboutSection.objects.create(
                section_key=key,
                title=title,
                body=body,
                order=i,
                is_active=True,
            )

    def _partners(self):
        if PartnerOffer.objects.exists():
            return
        offers = [
            (
                'Стратегия продвижения',
                'Помогаем выстроить эффективную стратегию вывода и роста бренда.',
            ),
            (
                'Логистика',
                'Организация поставок, склад и доставка по сети партнёров.',
            ),
            (
                'Маркетинговая поддержка',
                'Промо, трейд-маркетинг и digital-инструменты для роста продаж.',
            ),
            (
                'Консультации по продажам',
                'Работа с сетями, HoReCa и традиционной розницей.',
            ),
        ]
        for i, (title, text) in enumerate(offers):
            PartnerOffer.objects.create(
                title=title, text=text, order=i, is_active=True
            )

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
            safe_name = f'{product.brand.slug}-{product.pk or product.slug[:24]}.png'
            safe_name = ''.join(ch if ch.isascii() and (ch.isalnum() or ch in '-_.') else '-' for ch in safe_name)
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
        categories = [
            ('sauces', 'Соусы и маринады', 0),
            ('noodles', 'Макаронные изделия', 1),
            ('seaweed', 'Водорослевые продукты', 2),
            ('syrups', 'Сиропы', 3),
            ('chips', 'Чипсы', 4),
        ]
        cat_map = {}
        for slug, name, order in categories:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'order': order, 'is_active': True},
            )
            cat.is_active = True
            cat.name = name
            cat.order = order
            cat.save()
            cat_map[slug] = cat

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
            brand.name = name
            brand.order = order
            brand.is_featured = featured
            brand.is_active = True
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
            try:
                product, created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'brand': brand,
                        'category': category,
                        'name': row.get('name') or slug,
                        'package': row.get('package') or '',
                        'order': int(row.get('order') or 0),
                        'is_active': True,
                    },
                )
                product.brand = brand
                product.category = category
                product.name = row.get('name') or product.name
                product.package = row.get('package') or ''
                product.order = int(row.get('order') or 0)
                product.is_active = True
                # On Vercel UI serves static/img/catalog; skip heavy media copies.
                if not getattr(settings, 'IS_VERCEL', False):
                    self._ensure_product_image(
                        product,
                        image_name=row.get('image'),
                        force=False,
                    )
                product.save()
            except Exception as exc:  # noqa: BLE001 — keep seeding other rows
                self.stderr.write(f'Skip product {slug}: {exc}')

        if keep_slugs:
            Product.objects.exclude(slug__in=keep_slugs).update(is_active=False)
