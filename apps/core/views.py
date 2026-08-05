from django.shortcuts import render

from apps.catalog import selectors as catalog_selectors
from apps.catalog.models import Product

from . import selectors

_CATALOG_COLORS = (
    '#FF5A36',
    '#F79315',
    '#1FA968',
    '#3E7BFA',
    '#7C5CFC',
    '#FF4F97',
)


def _section_enabled(blocks, key: str, has_items: bool) -> bool:
    if not has_items:
        return False
    if key in blocks:
        return selectors.is_section_visible(blocks, key)
    return True


def _catalog_preview():
    categories = list(catalog_selectors.get_categories()[:6])
    preview = []
    for index, category in enumerate(categories):
        qs = Product.objects.filter(
            is_active=True,
            category=category,
            brand__is_active=True,
        ).select_related('brand').order_by('order', 'name')
        products = list(qs[:4])
        featured = next((p for p in products if p.image), None) or (
            qs.exclude(image='').exclude(image=None).first()
        ) or (products[0] if products else None)
        if featured and featured not in products and len(products) >= 5:
            products[-1] = featured
        elif featured and featured not in products:
            products.insert(0, featured)
        preview.append(
            {
                'category': category,
                'products': products,
                'featured': featured,
                'color': _CATALOG_COLORS[index % len(_CATALOG_COLORS)],
            }
        )
    return preview


def _home_context():
    blocks = selectors.get_blocks('home')
    advantages = list(selectors.get_advantages())
    stats = list(selectors.get_company_stats())
    retail_partners = selectors.get_retail_partners()
    brand_showcase = catalog_selectors.get_brands_for_showcase(featured_only=True)
    cases = list(selectors.get_case_studies())
    marquee = [f'{s.value} {s.label}' for s in stats] or ['AJERES']

    return {
        'blocks': blocks,
        'show_advantages': _section_enabled(
            blocks, 'advantages_visible', bool(advantages)
        ),
        'show_brands': _section_enabled(
            blocks, 'brands_visible', bool(retail_partners)
        ),
        'show_cases': _section_enabled(blocks, 'cases_visible', bool(cases)),
        'advantages': advantages,
        'stats': stats,
        'marquee_items': marquee * 4,
        'retail_partners': retail_partners,
        'brand_showcase': brand_showcase,
        'cases': cases,
        'catalog_preview': _catalog_preview(),
    }


def home(request):
    return render(request, 'pages/home.html', _home_context())


def about(request):
    blocks = selectors.get_blocks('about')
    sections = selectors.get_about_sections()
    stats = list(selectors.get_company_stats())
    return render(
        request,
        'pages/about.html',
        {
            'blocks': blocks,
            'sections': sections,
            'stats': stats,
        },
    )
