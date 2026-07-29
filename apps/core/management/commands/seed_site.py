"""Idempotent seed: settings, CMS blocks, categories, brands, sample products."""

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.catalog.models import Brand, Category, Product
from apps.catalog.selectors import invalidate_catalog_list_cache
from apps.core.import_content_data import (
    BRAND_LOGOS_DIR,
    BRANDS_SPEC,
    RETAIL_LOGOS_DIR,
    RETAIL_PARTNERS_SPEC,
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

# Minimal 1x1 PNG
_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
    b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
    b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)


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
        s.address = s.address or (
            'Ташкент, Мирзо-Улугбекский район, ул. Паркентская 327'
        )
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
        if Advantage.objects.exists():
            return
        data = [
            (
                'assortment',
                'Широкий ассортимент',
                '80+ товаров азиатской и специализированной бакалеи в одном каталоге.',
            ),
            (
                'brands',
                'Проверенные бренды',
                'Прямые контракты с производителями и контроль качества.',
            ),
            (
                'logistics',
                'Быстрая логистика',
                'Стабильные поставки и предсказуемые сроки для магазинов и HoReCa.',
            ),
            (
                'terms',
                'Гибкие условия',
                'Индивидуальные условия сотрудничества для партнёров.',
            ),
            (
                'experience',
                '7+ лет на рынке',
                'Опыт работы с розницей и HoReCa с 2018 года.',
            ),
        ]
        for i, (icon, title, text) in enumerate(data):
            Advantage.objects.create(
                icon_key=icon, title=title, text=text, order=i, is_active=True
            )

    def _stats(self):
        if CompanyStat.objects.exists():
            return
        for i, (value, label) in enumerate(
            [
                ('200+', 'партнёров'),
                ('80+', 'товаров в каталоге'),
                ('7+', 'лет на рынке'),
            ]
        ):
            CompanyStat.objects.create(
                value=value, label=label, order=i, is_active=True
            )

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
            cat_map[slug] = cat

        brand_map = {}
        for slug, name, logo_file, order, featured in BRANDS_SPEC:
            brand, created = Brand.objects.get_or_create(
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
            self._ensure_brand_logo(brand, logo_file, force=True)
            brand.save()
            brand_map[slug] = brand

        samples = [
            ('sen-soy', 'sauces', 'sous-chili-sladkiy-235', 'Соус «Сладкий Чили»', '235 гр.'),
            ('sen-soy', 'sauces', 'sous-chili-zhguchiy-235', 'Соус «Жгучий Чили»', '235 гр.'),
            ('sen-soy', 'sauces', 'sous-sriracha-310', 'Соус «Шрирача»', '310 гр.'),
            ('sen-soy', 'noodles', 'lapsha-somen-300', 'Лапша «Somen»', '300 гр.'),
            ('sen-soy', 'noodles', 'lapsha-udon-300', 'Пшеничная лапша «Udon»', '300 гр.'),
            ('sen-soy', 'seaweed', 'sushi-nori-28', 'Суши Нори', '28 гр.'),
            ('sen-soy', 'seaweed', 'chips-nori-original', 'Чипсы нори «Original»', '4,5 гр.'),
            ('riceup', 'chips', 'riceup-rice-chips-barbecue-60', 'Рисовые чипсы «Barbecue»', '60 гр.'),
            ('huligan', 'chips', 'huligan-pretzel-crush-cheese-65', 'Pretzel Crush «Cheese Sauce»', '65 гр.'),
            ('krambals', 'chips', 'krambals-bruschetta-tomato-mozzarella', 'Брускетта «Tomato & Mozzarella»', '70 гр.'),
        ]
        for brand_slug, cat_slug, slug, name, package in samples:
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'brand': brand_map[brand_slug],
                    'category': cat_map[cat_slug],
                    'name': name,
                    'package': package,
                    'is_active': True,
                },
            )
            if created or not product.image:
                self._ensure_image(product.image, f'{slug}.png')
                product.save()
