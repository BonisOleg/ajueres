"""Ідемпотентний seed фільтрів товару (іконки зі static, різні набори по брендах)."""

from __future__ import annotations

PRODUCT_FILTERS = (
    {
        'slug': 'natural-product',
        'order': 10,
        'name_ru': 'Натуральный продукт',
        'name_en': 'Natural product',
        'name_uz': 'Tabiiy mahsulot',
    },
    {
        'slug': 'gmo-free',
        'order': 20,
        'name_ru': 'Без ГМО',
        'name_en': 'Non-GMO',
        'name_uz': 'GMOsiz',
    },
    {
        'slug': 'palm-oil-free',
        'order': 30,
        'name_ru': 'Без пальмового масла',
        'name_en': 'Palm oil free',
        'name_uz': 'Palma yog‘isiz',
    },
    {
        'slug': 'healthy-snack',
        'order': 40,
        'name_ru': 'Полезный снэк',
        'name_en': 'Healthy snack',
        'name_uz': 'Foydali gazak',
    },
    {
        'slug': 'sugar-free',
        'order': 50,
        'name_ru': 'Без сахара',
        'name_en': 'No sugar',
        'name_uz': 'Shakarsiz',
    },
    {
        'slug': 'popped-never-fried',
        'order': 60,
        'name_ru': 'Открытые и никогда не жареные',
        'name_en': 'Popped and never fried',
        'name_uz': 'Portlatilgan, qovurilmagan',
    },
    {
        'slug': 'all-natural',
        'order': 70,
        'name_ru': 'Все натуральное',
        'name_en': 'All natural',
        'name_uz': 'To‘liq tabiiy',
    },
    {
        'slug': 'whole-grain',
        'order': 80,
        'name_ru': 'Цельно зерновое',
        'name_en': 'Whole grain',
        'name_uz': 'Butun don',
    },
    {
        'slug': 'gluten-free',
        'order': 90,
        'name_ru': 'Без глютена',
        'name_en': 'Gluten-free',
        'name_uz': 'Glutensiz',
    },
    {
        'slug': 'no-preservatives',
        'order': 100,
        'name_ru': 'Без консервантов',
        'name_en': 'No preservatives',
        'name_uz': 'Konservantsiz',
    },
    {
        'slug': 'no-msg',
        'order': 110,
        'name_ru': 'Без глутамата натрия',
        'name_en': 'No MSG',
        'name_uz': 'Natriy glutamatsiz',
    },
    {
        'slug': 'less-fat-60',
        'order': 120,
        'name_ru': 'На 60% меньше жира',
        'name_en': '60% less fat',
        'name_uz': '60% kam yog‘',
    },
    {
        'slug': 'popped-method',
        'order': 130,
        'name_ru': 'Взрывной способ приготовления',
        'name_en': 'Popped, not fried',
        'name_uz': 'Portlatib tayyorlangan',
    },
    {
        'slug': 'rich-in-fiber',
        'order': 140,
        'name_ru': 'Богаты клетчаткой',
        'name_en': 'Rich in fiber',
        'name_uz': 'Tola moddasiga boy',
    },
    {
        'slug': 'natural-yeast',
        'order': 150,
        'name_ru': 'Собственные натуральные дрожжи',
        'name_en': 'Natural yeast',
        'name_uz': 'Tabiiy xamirturush',
    },
    {
        'slug': 'slow-fermentation',
        'order': 160,
        'name_ru': 'Медленное брожение',
        'name_en': 'Slow fermentation',
        'name_uz': 'Sekin fermentatsiya',
    },
    {
        'slug': 'natural-flavors',
        'order': 170,
        'name_ru': 'Натуральные ароматизаторы',
        'name_en': 'Natural flavors',
        'name_uz': 'Tabiiy aromatizatorlar',
    },
    {
        'slug': 'natural-colors',
        'order': 180,
        'name_ru': 'Натуральные красители',
        'name_en': 'Natural colors',
        'name_uz': 'Tabiiy bo‘yoqlar',
    },
    {
        'slug': 'sourdough',
        'order': 190,
        'name_ru': 'На закваске',
        'name_en': 'Sourdough',
        'name_uz': 'Xamiruvala asosida',
    },
)

FILTER_SLUGS = {row['slug'] for row in PRODUCT_FILTERS}

SEN_SOY_FILTERS = (
    'natural-product',
    'gmo-free',
    'palm-oil-free',
    'healthy-snack',
    'sugar-free',
)
RICEUP_CHIPS_FILTERS = (
    'popped-never-fried',
    'all-natural',
    'whole-grain',
    'gluten-free',
    'gmo-free',
    'no-preservatives',
    'no-msg',
)
RICEUP_TORTILLA_FILTERS = (
    'less-fat-60',
    'popped-method',
    'rich-in-fiber',
    'gluten-free',
    'gmo-free',
    'no-msg',
    'no-preservatives',
)
KRAMBALS_FILTERS = (
    'natural-yeast',
    'slow-fermentation',
    'natural-flavors',
    'natural-colors',
    'palm-oil-free',
    'no-preservatives',
)
HULIGAN_FILTERS = (
    'sourdough',
    'palm-oil-free',
    'no-preservatives',
    'no-msg',
)

BRAND_FILTER_SLUGS: dict[str, tuple[str, ...]] = {
    'sen-soy': SEN_SOY_FILTERS,
    'paprichi': SEN_SOY_FILTERS,
    'yamchan': SEN_SOY_FILTERS,
    'riceup': tuple(dict.fromkeys((*RICEUP_CHIPS_FILTERS, *RICEUP_TORTILLA_FILTERS))),
    'krambals': KRAMBALS_FILTERS,
    'huligan': HULIGAN_FILTERS,
}


def filter_icon_static_path(slug: str) -> str:
    return f'img/product-filters/{slug}.png'


def _text(product) -> str:
    slug = (getattr(product, 'slug', '') or '').lower()
    name = (getattr(product, 'name', '') or '').lower()
    return f'{slug} {name}'


def filters_for_product(product) -> tuple[str, ...]:
    """Набір іконок/тегів за брендом (RiceUP — окремо чипси vs тортильї)."""
    brand = getattr(product, 'brand', None)
    brand_slug = getattr(brand, 'slug', '') or ''
    blob = _text(product)

    if brand_slug == 'riceup':
        if 'tortilla' in blob:
            return RICEUP_TORTILLA_FILTERS
        return RICEUP_CHIPS_FILTERS

    return BRAND_FILTER_SLUGS.get(brand_slug, ())


def ensure_product_filters() -> int:
    """Створює/оновлює фільтри; старі generic — деактивує."""
    from .models import ProductFilter

    created = 0
    keep = set()
    for row in PRODUCT_FILTERS:
        keep.add(row['slug'])
        obj, was_created = ProductFilter.objects.get_or_create(
            slug=row['slug'],
            defaults={
                'name': row['name_ru'],
                'name_ru': row['name_ru'],
                'name_en': row['name_en'],
                'name_uz': row['name_uz'],
                'order': row['order'],
                'is_active': True,
            },
        )
        if was_created:
            created += 1
            continue
        obj.name = row['name_ru']
        obj.name_ru = row['name_ru']
        obj.name_en = row['name_en']
        obj.name_uz = row['name_uz']
        obj.order = row['order']
        obj.is_active = True
        obj.save()
    ProductFilter.objects.exclude(slug__in=keep).update(is_active=False)
    return created


def ensure_product_filter_assignments() -> int:
    """Призначає фільтри за типом товару; ідемпотентно."""
    from .models import Product, ProductFilter

    ensure_product_filters()
    filters = {
        item.slug: item
        for item in ProductFilter.objects.filter(slug__in=FILTER_SLUGS)
    }
    updated = 0
    for product in Product.objects.select_related('brand'):
        slugs = filters_for_product(product)
        to_set = [filters[slug] for slug in slugs if slug in filters]
        before = set(product.extra_filters.values_list('pk', flat=True))
        after = {item.pk for item in to_set}
        if before == after:
            continue
        product.extra_filters.set(to_set)
        updated += 1
    return updated
