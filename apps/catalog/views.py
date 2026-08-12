from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_GET

from . import selectors


def _catalog_context(request):
    categories_selected = selectors.parse_category_slugs(
        request.GET.getlist('category')
    )
    features_selected = selectors.parse_category_slugs(
        request.GET.getlist('feature')
    )
    snacks_slugs = selectors.get_snacks_slugs()
    show_general_features = not selectors.selection_includes_snacks(
        categories_selected,
        snacks_slugs,
    )
    if not show_general_features:
        features_selected = []
    brand = (request.GET.get('brand') or '').strip() or None
    q = request.GET.get('q')
    page = request.GET.get('page', 1)

    products_qs = selectors.get_products(
        category_slugs=categories_selected,
        extra_filter_slugs=features_selected,
        brand_slug=brand,
        q=q,
    )
    page_obj = selectors.paginate_products(
        products_qs,
        page=page,
        per_page=getattr(settings, 'CATALOG_PER_PAGE', selectors.CATALOG_PER_PAGE),
    )
    grouped = selectors.group_by_brand(page_obj.object_list)

    resolved_cats, _ = selectors.resolve_categories_filter(categories_selected)
    active_parent_slugs: list[str] = []
    seen_parents: set[str] = set()
    for cat in resolved_cats:
        parent_slug = cat.parent.slug if cat.parent_id else cat.slug
        if parent_slug in seen_parents:
            continue
        seen_parents.add(parent_slug)
        active_parent_slugs.append(parent_slug)

    return {
        'categories': selectors.get_categories(),
        'grouped_products': grouped,
        'page_obj': page_obj,
        'paginator': page_obj.paginator,
        'active_categories': categories_selected,
        'active_category': categories_selected[0] if categories_selected else None,
        'active_parent_slugs': active_parent_slugs,
        'active_parent_slug': active_parent_slugs[0] if active_parent_slugs else None,
        'active_features': features_selected,
        'product_filters': (
            selectors.get_product_filters() if show_general_features else []
        ),
        'show_general_features': show_general_features,
        'snacks_slugs': snacks_slugs,
        'active_brand': brand,
        'search_q': selectors.normalize_search_query(q) or (q or '').strip(),
        'brands_showcase': selectors.get_brands_for_showcase(featured_only=True),
        'total_count': page_obj.paginator.count,
    }


@require_GET
def products(request):
    ctx = _catalog_context(request)
    is_htmx = request.headers.get('HX-Request') == 'true'
    ctx['hx_oob'] = is_htmx
    template = (
        'partials/catalog_results.html'
        if is_htmx
        else 'pages/products.html'
    )
    return render(request, template, ctx)
