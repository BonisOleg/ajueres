"""Seed eight product feature filters (idempotent)."""

from django.core.management.base import BaseCommand

from apps.catalog.product_filter_defaults import (
    ensure_product_filter_assignments,
    ensure_product_filters,
)


class Command(BaseCommand):
    help = 'Create default product feature filters if missing'

    def handle(self, *args, **options):
        created = ensure_product_filters()
        assigned = ensure_product_filter_assignments()
        self.stdout.write(
            self.style.SUCCESS(
                f'Product filters ready (created {created}, assigned {assigned})'
            )
        )
