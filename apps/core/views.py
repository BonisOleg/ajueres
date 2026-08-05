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


def _about_presentation(sections):
    """Prepare exact CMS copy for structured rendering without rewriting it."""
    by_key = {section.section_key: section for section in sections}
    for section in sections:
        section.presentation_paragraphs = [
            paragraph.strip()
            for paragraph in (section.body or '').split('\n\n')
            if paragraph.strip()
        ]

    market = by_key.get('market')
    market_intro = ''
    market_label = ''
    market_facts = []
    market_outro = []
    if market:
        lines = [line.strip() for line in (market.body or '').splitlines()]
        facts_started = False
        for line in lines:
            if not line:
                continue
            if line.startswith('•'):
                facts_started = True
                market_facts.append(line.removeprefix('•').strip())
            elif not market_intro:
                market_intro = line
            elif not facts_started and not market_label:
                market_label = line
            else:
                market_outro.append(line)

    return {
        'about_section': by_key.get('about'),
        'mission_section': by_key.get('mission'),
        'goals_section': by_key.get('goals') or by_key.get('vision'),
        'value_sections': [
            section
            for key in ('philosophy', 'analytics', 'responsibility')
            if (section := by_key.get(key))
        ],
        'market_section': market,
        'market_intro': market_intro,
        'market_label': market_label,
        'market_facts': market_facts,
        'market_outro': market_outro,
    }


def about(request):
    blocks = selectors.get_blocks('about')
    sections = list(selectors.get_about_sections())
    stats = list(selectors.get_company_stats())
    presentation = _about_presentation(sections)
    return render(
        request,
        'pages/about.html',
        {
            'blocks': blocks,
            'sections': sections,
            'stats': stats,
            **presentation,
        },
    )
