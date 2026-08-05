"""Перебудова Product.search_text (після імпорту даних або зміни нормалізації)."""

from django.core.management.base import BaseCommand

from apps.catalog.models import Product, refresh_products_search_text


class Command(BaseCommand):
    help = 'Перебудовує пошуковий текст усіх товарів каталогу.'

    def handle(self, *args, **options):
        total = Product.objects.count()
        changed = refresh_products_search_text(Product.objects.all())
        self.stdout.write(
            self.style.SUCCESS(f'search_text: оновлено {changed} з {total} товарів')
        )
