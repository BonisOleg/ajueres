from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.catalog.models import Brand, Category, Product, ProductFilter
from apps.catalog.product_filter_defaults import (
    ensure_product_filter_assignments,
    ensure_product_filters,
)
from apps.catalog.selectors import (
    get_brands_for_showcase,
    get_product,
    get_product_filters,
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

    def test_get_product_by_slug(self):
        found = get_product('sauce-0')
        self.assertIsNotNone(found)
        self.assertEqual(found.slug, 'sauce-0')
        missing = Product.objects.get(slug='sauce-1')
        missing.is_active = False
        missing.save(update_fields=['is_active'])
        self.assertIsNone(get_product('sauce-1'))
        self.assertIsNone(get_product('nope'))

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

    def test_multiple_categories_use_or_logic(self):
        noodles = Category.objects.create(slug='noodles', name='Лапша', order=2)
        Product.objects.create(
            brand=self.brand,
            category=noodles,
            slug='noodle-1',
            name='Udon',
            name_ru='Udon',
            package='300 гр.',
            package_ru='300 гр.',
            image=_tiny_png(),
        )
        self.assertEqual(
            get_products(category_slugs=['sauces', 'noodles']).count(),
            4,
        )
        self.assertEqual(
            get_products(category_slugs='sauces,noodles').count(),
            4,
        )


class ProductFilterSelectorsTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(slug='sauces', name='Соусы')
        self.brand = Brand.objects.create(slug='sen-soy', name='Sen Soy')
        self.gluten = ProductFilter.objects.create(
            slug='gluten-free',
            name='Без глютена',
            order=10,
        )
        self.palm = ProductFilter.objects.create(
            slug='palm-oil-free',
            name='Без пальмового масла',
            order=20,
        )
        self.with_gluten = Product.objects.create(
            brand=self.brand,
            category=self.cat,
            slug='sauce-gf',
            name='Соус без глютена',
            name_ru='Соус без глютена',
            package='235 гр.',
            package_ru='235 гр.',
            image=_tiny_png(),
        )
        self.with_gluten.extra_filters.add(self.gluten)
        self.plain = Product.objects.create(
            brand=self.brand,
            category=self.cat,
            slug='sauce-plain',
            name='Соус обычный',
            name_ru='Соус обычный',
            package='235 гр.',
            package_ru='235 гр.',
            image=_tiny_png(),
        )

    def test_filter_by_feature_slug(self):
        qs = get_products(extra_filter_slugs=['gluten-free'])
        self.assertEqual(list(qs), [self.with_gluten])

    def test_feature_or_logic(self):
        self.plain.extra_filters.add(self.palm)
        qs = get_products(extra_filter_slugs=['gluten-free', 'palm-oil-free'])
        self.assertEqual(set(qs), {self.with_gluten, self.plain})

    def test_inactive_feature_hidden(self):
        self.gluten.is_active = False
        self.gluten.save()
        self.assertEqual(get_products(extra_filter_slugs=['gluten-free']).count(), 0)
        names = [item.slug for item in get_product_filters(brand_slug='sen-soy')]
        self.assertNotIn('gluten-free', names)

    def test_ensure_seed_is_idempotent(self):
        first = ensure_product_filters()
        second = ensure_product_filters()
        self.assertGreaterEqual(first, 6)
        self.assertEqual(second, 0)
        self.assertGreaterEqual(ProductFilter.objects.count(), 8)

    def test_assign_filters_to_known_products(self):
        rice_paper = Product.objects.create(
            brand=self.brand,
            category=self.cat,
            slug='sen-soy-rice-paper-100-18',
            name='«Рисова бумага»',
            name_ru='«Рисова бумага»',
            package='100 гр.',
            package_ru='100 гр.',
            image=_tiny_png(),
        )
        first = ensure_product_filter_assignments()
        second = ensure_product_filter_assignments()
        slugs = set(rice_paper.extra_filters.values_list('slug', flat=True))
        self.assertGreaterEqual(first, 1)
        self.assertEqual(second, 0)
        self.assertEqual(
            slugs,
            {
                'natural-product',
                'gmo-free',
                'palm-oil-free',
                'healthy-snack',
                'sugar-free',
            },
        )

    def test_catalog_page_hides_filters_without_brand(self):
        from django.urls import reverse

        ensure_product_filters()
        gf = ProductFilter.objects.get(slug='gluten-free')
        self.with_gluten.extra_filters.add(gf)
        response = self.client.get(reverse('products'))
        html = response.content.decode()
        self.assertRegex(html, r'id="catalog-features"[^>]*\bhidden\b')
        self.assertNotIn('catalog-feature__icon', html)

    def test_catalog_page_shows_brand_filter_icons(self):
        from django.urls import reverse

        ensure_product_filters()
        response = self.client.get(reverse('products'), {'brand': 'sen-soy'})
        self.assertContains(response, 'catalog-features')
        self.assertContains(response, 'catalog-feature__icon')
        self.assertContains(response, 'natural-product')

    def test_feature_filter_includes_snacks(self):
        snacks = Category.objects.create(slug='snacks', name='Снеки', order=10)
        chips = Category.objects.create(
            slug='chips', name='Чипсы', parent=snacks, order=0
        )
        snack = Product.objects.create(
            brand=self.brand,
            category=chips,
            slug='nori-chips',
            name='Чипсы нори',
            name_ru='Чипсы нори',
            package='4,5 гр.',
            package_ru='4,5 гр.',
            image=_tiny_png(),
        )
        snack.extra_filters.add(self.gluten)
        qs = get_products(extra_filter_slugs=['gluten-free'])
        self.assertEqual(set(qs), {self.with_gluten, snack})

    def test_snacks_category_hides_general_feature_row(self):
        from django.urls import reverse

        ensure_product_filters()
        Category.objects.create(slug='snacks', name='Снеки', order=10)
        response = self.client.get(reverse('products'), {'category': 'snacks'})
        html = response.content.decode()
        self.assertRegex(html, r'id="catalog-features"[^>]*\bhidden\b')
        self.assertNotIn('catalog-feature__icon', html)


class CatalogAdminImagePreviewTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from django.urls import reverse

        self.reverse = reverse
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'owner',
            'owner@ajeres.uz',
            'OldPass123!',
        )
        self.client.force_login(self.user)

    def test_filter_icon_shows_static_fallback_preview(self):
        ensure_product_filters()
        filt = ProductFilter.objects.get(slug='natural-product')
        response = self.client.get(
            self.reverse('admin:catalog_productfilter_change', args=[filt.pk]),
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('img/product-filters/natural-product.png', content)
        self.assertIn('admin-image-preview', content)

    def test_product_change_form_has_image_preview_widget(self):
        cat = Category.objects.create(slug='sauces', name='Соусы')
        brand = Brand.objects.create(
            slug='sen-soy',
            name='Sen Soy',
            logo=_tiny_png(),
        )
        product = Product.objects.create(
            brand=brand,
            category=cat,
            slug='sauce-preview',
            name='Соус',
            name_ru='Соус',
            package='235 гр.',
            image=_tiny_png(),
        )
        response = self.client.get(
            self.reverse('admin:catalog_product_change', args=[product.pk]),
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('admin-image-preview', content)
        self.assertIn('accept="image/jpeg,image/png,image/webp,image/gif"', content)

