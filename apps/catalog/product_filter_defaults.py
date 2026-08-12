"""Ідемпотентний seed додаткових фільтрів товару (іконки зі static)."""

from __future__ import annotations

PRODUCT_FILTERS = (
    {
        'slug': 'natural',
        'order': 10,
        'name_ru': 'Натуральные ингредиенты',
        'name_en': 'Natural ingredients',
        'name_uz': 'Tabiiy ingredientlar',
    },
    {
        'slug': 'palm-oil-free',
        'order': 20,
        'name_ru': 'Без пальмового масла',
        'name_en': 'Palm oil free',
        'name_uz': 'Palma yog‘isiz',
    },
    {
        'slug': 'no-preservatives',
        'order': 30,
        'name_ru': 'Без консервантов',
        'name_en': 'No preservatives',
        'name_uz': 'Konservantsiz',
    },
    {
        'slug': 'cruelty-free',
        'order': 40,
        'name_ru': 'Без тестов на животных',
        'name_en': 'Cruelty-free',
        'name_uz': 'Hayvonlarda sinovsiz',
    },
    {
        'slug': 'gluten-free',
        'order': 50,
        'name_ru': 'Без глютена',
        'name_en': 'Gluten-free',
        'name_uz': 'Glutensiz',
    },
    {
        'slug': 'certified',
        'order': 60,
        'name_ru': 'Сертифицировано',
        'name_en': 'Certified',
        'name_uz': 'Sertifikatlangan',
    },
    {
        'slug': 'recyclable',
        'order': 70,
        'name_ru': 'Перерабатываемая упаковка',
        'name_en': 'Recyclable',
        'name_uz': 'Qayta ishlanadigan',
    },
    {
        'slug': 'natural-origin',
        'order': 80,
        'name_ru': 'Натуральное происхождение',
        'name_en': 'Natural origin',
        'name_uz': 'Tabiiy kelib chiqish',
    },
)

FILTER_SLUGS = {row['slug'] for row in PRODUCT_FILTERS}

# slug товару → фільтри (add, не знімає інші призначення з адмінки)
PRODUCT_FILTER_ASSIGNMENTS = {
    'sen-soy-rice-paper-100-18': (
        'gluten-free',
        'palm-oil-free',
        'no-preservatives',
        'natural',
    ),
    'sen-soy-sushi-nori-28-4': (
        'gluten-free',
        'palm-oil-free',
        'no-preservatives',
        'natural',
    ),
    'sen-soy-rice-vermicelli-noodle-300-15': ('gluten-free',),
    'sen-soy-fo-kho-noodle-200-16': ('gluten-free',),
    'sen-soy-rice-vinegar-220-27': ('gluten-free',),
}


def filter_icon_static_path(slug: str) -> str:
    return f'img/product-filters/{slug}.png'


def ensure_product_filters() -> int:
    """Створює 8 фільтрів, не перезаписує вже змінені назви."""
    from .models import ProductFilter

    created = 0
    for row in PRODUCT_FILTERS:
        _, was_created = ProductFilter.objects.get_or_create(
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
    return created


def ensure_product_filter_assignments() -> int:
    """Призначає фільтри за slug; ідемпотентно, не знімає ручні."""
    from .models import Product, ProductFilter

    ensure_product_filters()
    filters = {
        item.slug: item
        for item in ProductFilter.objects.filter(slug__in=FILTER_SLUGS)
    }
    updated = 0
    for product_slug, filter_slugs in PRODUCT_FILTER_ASSIGNMENTS.items():
        product = Product.objects.filter(slug=product_slug).first()
        if product is None:
            continue
        to_add = [filters[slug] for slug in filter_slugs if slug in filters]
        if not to_add:
            continue
        before = set(product.extra_filters.values_list('pk', flat=True))
        product.extra_filters.add(*to_add)
        after = set(product.extra_filters.values_list('pk', flat=True))
        if after != before:
            updated += 1
    return updated
