from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_GET

from . import selectors


def _catalog_context(request):
    category = (request.GET.get('category') or '').strip() or None
    brand = (request.GET.get('brand') or '').strip() or None
    q = request.GET.get('q')
    page = request.GET.get('page', 1)

    products_qs = selectors.get_products(
        category_slug=category,
        brand_slug=brand,
        q=q,
    )
    page_obj = selectors.paginate_products(
        products_qs,
        page=page,
        per_page=getattr(settings, 'CATALOG_PER_PAGE', selectors.CATALOG_PER_PAGE),
    )
    grouped = selectors.group_by_brand(page_obj.object_list)

    return {
        'categories': selectors.get_categories(),
        'grouped_products': grouped,
        'page_obj': page_obj,
        'paginator': page_obj.paginator,
        'active_category': category,
        'active_brand': brand,
        'search_q': selectors.normalize_search_query(q) or (q or '').strip(),
        'brands_showcase': selectors.get_brands_for_showcase(featured_only=True),
        'total_count': page_obj.paginator.count,
    }


@require_GET
def products(request):
    ctx = _catalog_context(request)
    template = (
        'partials/catalog_results.html'
        if request.headers.get('HX-Request') == 'true'
        else 'pages/products.html'
    )
    return render(request, template, ctx)
