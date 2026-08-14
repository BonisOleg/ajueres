"""Публічні селектори каталогу: бренди, категорії, товари, пагінація."""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Iterable

from django.core.cache import cache
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import Prefetch, Q, QuerySet

from .models import Brand, Category, Product, ProductFilter
from .search import SEARCH_MAX_LEN, SEARCH_MIN_LEN, tokenize

CATALOG_PER_PAGE = 72
SNACKS_ROOT_SLUG = 'snacks'
_WHITESPACE_RE = re.compile(r'\s+')

_CACHE_BRANDS_ALL = 'brands_public:all'
_CACHE_BRANDS_FEATURED = 'brands_public:featured'
_CACHE_TTL = 60 * 10


def normalize_search_query(q: str | None) -> str:
    """Strip, схлопнути пробіли, min 2 / max 100. Інакше — порожній рядок."""
    if not q:
        return ''
    normalized = _WHITESPACE_RE.sub(' ', q.strip())
    if len(normalized) < SEARCH_MIN_LEN:
        return ''
    return normalized[:SEARCH_MAX_LEN]


def parse_page_number(raw) -> int:
    """Невалідний page → 1."""
    try:
        page = int(raw)
    except (TypeError, ValueError):
        return 1
    return page if page >= 1 else 1


def get_brands_for_showcase(*, featured_only: bool = False) -> list[Brand]:
    """
    Виробники для блоку під каталогом на /products.
    featured_only=True — лише is_featured (типовий showcase).
    """
    cache_key = _CACHE_BRANDS_FEATURED if featured_only else _CACHE_BRANDS_ALL
    cached_ids = cache.get(cache_key)
    base = Brand.objects.filter(is_active=True).order_by('order', 'name')

    if cached_ids is not None:
        by_id = {b.pk: b for b in base.filter(pk__in=cached_ids)}
        return [by_id[pk] for pk in cached_ids if pk in by_id]

    if featured_only:
        featured = list(base.filter(is_featured=True))
        brands = featured if featured else list(base)
    else:
        brands = list(base)

    cache.set(cache_key, [b.pk for b in brands], timeout=_CACHE_TTL)
    return brands


def _children_prefetch() -> Prefetch:
    return Prefetch(
        'children',
        queryset=Category.objects.filter(is_active=True).order_by('order', 'name'),
    )


def get_categories() -> list[Category]:
    """Кореневі активні категорії з prefetch дітей для фільтра."""
    return list(
        Category.objects.filter(is_active=True, parent__isnull=True)
        .prefetch_related(_children_prefetch())
        .order_by('order', 'name')
    )


def parse_category_slugs(raw_values: Iterable[str] | str | None) -> list[str]:
    """Нормалізує category з GET: getlist, comma-separated, без дублікатів."""
    if raw_values is None:
        return []
    if isinstance(raw_values, str):
        values = [raw_values]
    else:
        values = list(raw_values)

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        for part in str(value).split(','):
            slug = part.strip()
            if not slug or slug in seen:
                continue
            seen.add(slug)
            result.append(slug)
    return result


def resolve_category_filter(
    category_slug: str | None,
) -> tuple[Category | None, list[str]]:
    """
    Повертає (категорія, список slug для фільтра товарів).
    Для батька — slug батька + активних нащадків.
    """
    if not category_slug:
        return None, []
    cat = (
        Category.objects.filter(is_active=True, slug=category_slug)
        .select_related('parent')
        .prefetch_related(_children_prefetch())
        .first()
    )
    if not cat:
        return None, [category_slug]
    child_slugs = [c.slug for c in cat.children.all()]
    if child_slugs:
        return cat, [cat.slug, *child_slugs]
    return cat, [cat.slug]


def resolve_categories_filter(
    category_slugs: Iterable[str] | str | None,
) -> tuple[list[Category], list[str]]:
    """Об'єднує кілька категорій (OR): батьки розгортаються в дітей."""
    slugs = parse_category_slugs(category_slugs)
    if not slugs:
        return [], []

    categories: list[Category] = []
    product_slugs: list[str] = []
    seen_cats: set[str] = set()
    seen_products: set[str] = set()

    for slug in slugs:
        cat, resolved = resolve_category_filter(slug)
        if cat and cat.slug not in seen_cats:
            seen_cats.add(cat.slug)
            categories.append(cat)
        for item in resolved:
            if item in seen_products:
                continue
            seen_products.add(item)
            product_slugs.append(item)
    return categories, product_slugs


def get_snacks_slugs() -> set[str]:
    """Slug кореневої «Снеки» та всіх прямих нащадків."""
    slugs = {SNACKS_ROOT_SLUG}
    children = Category.objects.filter(
        is_active=True,
        parent__slug=SNACKS_ROOT_SLUG,
    ).values_list('slug', flat=True)
    slugs.update(children)
    return slugs


def selection_includes_snacks(
    category_slugs: Iterable[str] | str | None,
    snacks_slugs: set[str] | None = None,
) -> bool:
    selected = parse_category_slugs(category_slugs)
    if not selected:
        return False
    snacks = snacks_slugs if snacks_slugs is not None else get_snacks_slugs()
    return any(slug in snacks for slug in selected)


def get_product_filters(*, brand_slug: str | None = None) -> list[ProductFilter]:
    """Фільтри каталогу: лише для вибраного бренду, у фіксованому порядку."""
    from .product_filter_defaults import BRAND_FILTER_SLUGS

    brand = (brand_slug or '').strip()
    slugs = BRAND_FILTER_SLUGS.get(brand)
    if not slugs:
        return []
    found = {
        item.slug: item
        for item in ProductFilter.objects.filter(is_active=True, slug__in=slugs)
    }
    return [found[slug] for slug in slugs if slug in found]


def get_products(
    *,
    category_slug: str | None = None,
    category_slugs: Iterable[str] | str | None = None,
    extra_filter_slugs: Iterable[str] | str | None = None,
    brand_slug: str | None = None,
    q: str | None = None,
) -> QuerySet[Product]:
    qs = (
        Product.objects.filter(
            is_active=True,
            brand__is_active=True,
            category__is_active=True,
        )
        .select_related('brand', 'category', 'category__parent')
        .prefetch_related(
            Prefetch(
                'extra_filters',
                queryset=ProductFilter.objects.filter(is_active=True).order_by(
                    'order', 'name'
                ),
            )
        )
        .order_by('brand__order', 'order', 'name')
    )

    selected = parse_category_slugs(category_slugs)
    if category_slug:
        selected = parse_category_slugs([*selected, category_slug])
    if selected:
        _, slugs = resolve_categories_filter(selected)
        if slugs:
            qs = qs.filter(category__slug__in=slugs)
    if brand_slug:
        qs = qs.filter(brand__slug=brand_slug)

    features = parse_category_slugs(extra_filter_slugs)
    if features:
        qs = qs.filter(
            extra_filters__slug__in=features,
            extra_filters__is_active=True,
        ).distinct()

    search_q = build_product_search_q(normalize_search_query(q))
    if search_q is not None:
        qs = qs.filter(search_q)

    return qs


def get_product(slug: str) -> Product | None:
    """Публічний товар за slug або None (404 на view)."""
    slug = (slug or '').strip()
    if not slug:
        return None
    return get_products().filter(slug=slug).first()


def build_product_search_q(query: str) -> Q | None:
    """
    Кожне слово запиту має входити в `Product.search_text` (AND).

    search_text уже нормалізований (нижній регістр, без лапок і пунктуації),
    тому `contains` працює однаково на SQLite і PostgreSQL, у т.ч. для кирилиці.
    """
    tokens = tokenize(query)
    if not tokens:
        return None
    condition = Q()
    for token in tokens:
        condition &= Q(search_text__contains=token)
    return condition


def paginate_products(
    qs: QuerySet[Product],
    *,
    page: int | str | None = 1,
    per_page: int = CATALOG_PER_PAGE,
) -> Page:
    paginator = Paginator(qs, per_page)
    page_number = parse_page_number(page)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages or 1)


def group_by_brand(products: Iterable[Product]) -> OrderedDict[Brand, list[Product]]:
    """Групує товари поточної сторінки по бренду (порядок збереження)."""
    grouped: OrderedDict[Brand, list[Product]] = OrderedDict()
    for product in products:
        grouped.setdefault(product.brand, []).append(product)
    return grouped


def invalidate_catalog_list_cache() -> None:
    cache.delete_many([
        _CACHE_BRANDS_ALL,
        _CACHE_BRANDS_FEATURED,
    ])
