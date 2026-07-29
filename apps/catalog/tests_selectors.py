from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.catalog.models import Brand, Category, Product
from apps.catalog.selectors import (
    get_brands_for_showcase,
    get_products,
    group_by_brand,
    normalize_search_query,
    paginate_products,
    parse_page_number,
)


def _tiny_png():
    return SimpleUploadedFile(
        't.png',
        (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
            b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
            b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        ),
        content_type='image/png',
    )


class CatalogSelectorsTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(slug='sauces', name='Соусы')
        self.brand = Brand.objects.create(
            slug='sen-soy',
            name='Sen Soy',
            logo=_tiny_png(),
            is_featured=True,
        )
        Brand.objects.create(
            slug='chester',
            name='Chester',
            logo=_tiny_png(),
            is_featured=False,
            order=2,
        )
        for i in range(3):
            Product.objects.create(
                brand=self.brand,
                category=self.cat,
                slug=f'sauce-{i}',
                name=f'Соус Чили {i}',
                name_ru=f'Соус Чили {i}',
                package='235 гр.',
                package_ru='235 гр.',
                image=_tiny_png(),
                order=i,
            )

    def test_normalize_search(self):
        self.assertEqual(normalize_search_query('  а  '), '')
        self.assertEqual(normalize_search_query('чили'), 'чили')
        self.assertEqual(normalize_search_query('  сладкий   чили '), 'сладкий чили')

    def test_parse_page(self):
        self.assertEqual(parse_page_number('abc'), 1)
        self.assertEqual(parse_page_number(0), 1)
        self.assertEqual(parse_page_number('3'), 3)

    def test_featured_brands_fallback(self):
        Brand.objects.all().update(is_featured=False)
        brands = get_brands_for_showcase(featured_only=True)
        self.assertEqual(len(brands), 2)

    def test_search_and_filter(self):
        qs = get_products(category_slug='sauces', q='Чили')
        self.assertEqual(qs.count(), 3)
        self.assertEqual(get_products(category_slug='chips').count(), 0)
        self.assertEqual(get_products(q='Sen').count(), 3)

    def test_paginate_and_group(self):
        page = paginate_products(get_products(), page=1, per_page=2)
        self.assertEqual(len(page.object_list), 2)
        grouped = group_by_brand(page.object_list)
        self.assertIn(self.brand, grouped)
