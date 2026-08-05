"""Публічні селектори каталогу: бренди, категорії, товари, пагінація."""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Iterable

from django.core.cache import cache
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import Prefetch, Q, QuerySet

from .models import Brand, Category, Product
from .search import SEARCH_MAX_LEN, SEARCH_MIN_LEN, tokenize

CATALOG_PER_PAGE = 24
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


def get_products(
    *,
    category_slug: str | None = None,
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
        .order_by('brand__order', 'order', 'name')
    )

    if category_slug:
        _, slugs = resolve_category_filter(category_slug)
        if slugs:
            qs = qs.filter(category__slug__in=slugs)
    if brand_slug:
        qs = qs.filter(brand__slug=brand_slug)

    search_q = build_product_search_q(normalize_search_query(q))
    if search_q is not None:
        qs = qs.filter(search_q)

    return qs


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
