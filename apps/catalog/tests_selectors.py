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

    def test_search_is_case_insensitive_for_cyrillic(self):
        self.assertEqual(get_products(q='чили').count(), 3)
        self.assertEqual(get_products(q='ЧИЛИ').count(), 3)

    def test_search_ignores_quotes_and_word_order(self):
        product = Product.objects.create(
            brand=self.brand,
            category=self.cat,
            slug='rice-paper-1',
            name='«Рисова бумага»',
            name_ru='«Рисова бумага»',
            package='100 гр.',
            package_ru='100 гр.',
            image=_tiny_png(),
        )
        for query in (
            'рисова бумага',
            '"Рисова бумага"',
            'бумага рисова',
            'рисова 100',
            'sen soy бумага',
        ):
            with self.subTest(query=query):
                self.assertIn(product, get_products(q=query))

    def test_search_requires_all_tokens(self):
        self.assertEqual(get_products(q='чили нори').count(), 0)

    def test_search_matches_category_name(self):
        self.assertEqual(get_products(q='соусы').count(), 3)

    def test_search_text_updates_on_brand_rename(self):
        self.brand.name = 'Сэн Сой'
        self.brand.save()
        self.assertEqual(get_products(q='сэн сой').count(), 3)

    def test_paginate_and_group(self):
        page = paginate_products(get_products(), page=1, per_page=2)
        self.assertEqual(len(page.object_list), 2)
        grouped = group_by_brand(page.object_list)
        self.assertIn(self.brand, grouped)

    def test_parent_category_includes_children(self):
        snacks = Category.objects.create(slug='snacks', name='Снеки', order=10)
        chips = Category.objects.create(
            slug='chips', name='Чипсы', parent=snacks, order=0
        )
        crush = Category.objects.create(
            slug='crush', name='Краш', parent=snacks, order=1
        )
        Product.objects.create(
            brand=self.brand,
            category=chips,
            slug='chip-1',
            name='Рисовые чипсы',
            name_ru='Рисовые чипсы',
            package='50 гр.',
            package_ru='50 гр.',
            image=_tiny_png(),
        )
        Product.objects.create(
            brand=self.brand,
            category=crush,
            slug='crush-1',
            name='Pretzel Crush',
            name_ru='Pretzel Crush',
            package='70 гр.',
            package_ru='70 гр.',
            image=_tiny_png(),
        )
        self.assertEqual(get_products(category_slug='snacks').count(), 2)
        self.assertEqual(get_products(category_slug='chips').count(), 1)
        self.assertEqual(get_products(category_slug='crush').count(), 1)
