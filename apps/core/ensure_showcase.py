"""Idempotent partners/brands for Vercel (no overwrite of editor data)."""

from apps.catalog.models import Brand
from apps.core.import_content_data import BRANDS_SPEC, RETAIL_PARTNERS_SPEC
from apps.core.models import RetailPartner


def ensure_showcase() -> None:
    for slug, name, _logo, order in RETAIL_PARTNERS_SPEC:
        RetailPartner.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'order': order,
                'is_active': True,
            },
        )

    for slug, name, _logo, order, featured in BRANDS_SPEC:
        Brand.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'order': order,
                'is_active': True,
                'is_featured': featured,
            },
        )
