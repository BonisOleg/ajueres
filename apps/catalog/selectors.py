"""Публічні селектори каталогу: бренди, категорії, товари, пагінація."""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Iterable, NamedTuple

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


def category_family_maps(
    categories: Iterable[Category] | None = None,
) -> tuple[dict[str, str], dict[str, list[str]]]:
    """parent_of[child]=parent, children_of[parent]=[child, …] з коренів фільтра."""
    roots = list(categories) if categories is not None else get_categories()
    parent_of: dict[str, str] = {}
    children_of: dict[str, list[str]] = {}
    for cat in roots:
        kids = [child.slug for child in cat.children.all()]
        if not kids:
            continue
        children_of[cat.slug] = kids
        for kid in kids:
            parent_of[kid] = cat.slug
    return parent_of, children_of


def toggle_category_selection(
    selected: Iterable[str] | str | None,
    slug: str | None,
    *,
    categories: Iterable[Category] | None = None,
    parent_of: dict[str, str] | None = None,
    children_of: dict[str, list[str]] | None = None,
) -> list[str]:
    """
    Toggle категорії без «батько + дитина»:
    дитина замінює батька і сестер; вимкнення останньої дитини повертає батька.
    Корені лишаються OR multi-select.
    """
    current = parse_category_slugs(selected)
    target = (slug or '').strip()
    if not target:
        return current
    if parent_of is None or children_of is None:
        parent_of, children_of = category_family_maps(categories)

    parent = parent_of.get(target)
    siblings = list(children_of.get(parent, [])) if parent else []
    kids = list(children_of.get(target, []))

    if target in current:
        remaining = [item for item in current if item != target]
        if (
            parent
            and parent not in remaining
            and not any(sib in remaining for sib in siblings)
        ):
            remaining.append(parent)
        return remaining

    drop: set[str] = set(kids)
    if parent:
        drop.add(parent)
        drop.update(siblings)
    remaining = [item for item in current if item not in drop]
    remaining.append(target)
    return remaining


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
    from .product_filter_defaults import BRAND_FILTER_SLUGS, ensure_product_filters

    brand = (brand_slug or '').strip()
    slugs = BRAND_FILTER_SLUGS.get(brand)
    if not slugs:
        return []

    def _ordered() -> list[ProductFilter]:
        found = {
            item.slug: item
            for item in ProductFilter.objects.filter(is_active=True, slug__in=slugs)
        }
        return [found[slug] for slug in slugs if slug in found]

    rows = _ordered()
    if len(rows) < len(slugs):
        ensure_product_filters()
        rows = _ordered()
    return rows


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
    product = get_products().filter(slug=slug).first()
    if product is not None:
        _ensure_product_extra_filters(product)
    return product


def _ensure_product_extra_filters(product: Product) -> None:
    """Якщо теги порожні — підставити набір бренду (самолікування пропущеного seed)."""
    from .product_filter_defaults import FILTER_SLUGS, ensure_product_filters, filters_for_product

    if product.extra_filters.exists():
        return
    slugs = filters_for_product(product)
    if not slugs:
        return
    ensure_product_filters()
    filters = {
        item.slug: item
        for item in ProductFilter.objects.filter(slug__in=FILTER_SLUGS)
    }
    to_set = [filters[item] for item in slugs if item in filters]
    if to_set:
        product.extra_filters.set(to_set)
        cache = getattr(product, '_prefetched_objects_cache', None)
        if cache is not None:
            cache.pop('extra_filters', None)


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


class CatalogProductGroup(NamedTuple):
    brand: Brand
    products: list[Product]
    kind: str
    badges: tuple[ProductFilter, ...]


def _product_is_snack(product: Product, snacks_slugs: set[str]) -> bool:
    category = getattr(product, 'category', None)
    if category is None:
        return False
    if category.slug in snacks_slugs:
        return True
    parent = getattr(category, 'parent', None)
    return bool(parent and parent.slug in snacks_slugs)


def _badges_for_product(product: Product) -> tuple[ProductFilter, ...]:
    from .product_filter_defaults import SNACK_BADGE_BRANDS, filters_for_product

    brand_slug = getattr(getattr(product, 'brand', None), 'slug', '') or ''
    if brand_slug not in SNACK_BADGE_BRANDS:
        return ()
    slugs = filters_for_product(product)
    if not slugs:
        return ()
    found = {
        item.slug: item
        for item in product.extra_filters.all()
        if getattr(item, 'is_active', True)
    }
    ordered = tuple(found[slug] for slug in slugs if slug in found)
    if len(ordered) == len(slugs):
        return ordered
    fallback = {
        item.slug: item
        for item in ProductFilter.objects.filter(is_active=True, slug__in=slugs)
    }
    return tuple(fallback[slug] for slug in slugs if slug in fallback)


def group_catalog_products(
    products: Iterable[Product],
    *,
    snacks_slugs: set[str] | None = None,
) -> list[CatalogProductGroup]:
    """Групи каталогу: бренд, RiceUP чипси/тортильї окремо, значки лише для снеків."""
    from .product_filter_defaults import riceup_line

    snacks = snacks_slugs if snacks_slugs is not None else get_snacks_slugs()
    buckets: OrderedDict[tuple[int, str], list[Product]] = OrderedDict()
    for product in products:
        kind = riceup_line(product)
        buckets.setdefault((product.brand_id, kind), []).append(product)

    groups: list[CatalogProductGroup] = []
    for items in buckets.values():
        show_badges = all(_product_is_snack(item, snacks) for item in items)
        groups.append(
            CatalogProductGroup(
                brand=items[0].brand,
                products=items,
                kind=riceup_line(items[0]),
                badges=_badges_for_product(items[0]) if show_badges else (),
            )
        )
    return groups


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
