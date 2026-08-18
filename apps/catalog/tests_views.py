from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Brand, Category, Product, ProductFilter
from apps.catalog.product_filter_defaults import (
    ensure_product_filter_assignments,
    ensure_product_filters,
)
from apps.catalog.selectors import toggle_category_selection
from apps.catalog.tests_selectors import _tiny_png
from apps.core.models import SiteSettings


class ProductDetailViewTests(TestCase):
    def setUp(self):
        SiteSettings.load()
        self.cat = Category.objects.create(slug='sauces', name='Соусы')
        self.brand = Brand.objects.create(
            slug='sen-soy',
            name='Sen Soy',
            logo=_tiny_png(),
        )
        self.filter = ProductFilter.objects.create(
            slug='gluten-free',
            name='Без глютена',
        )
        self.product = Product.objects.create(
            brand=self.brand,
            category=self.cat,
            slug='chili-sauce',
            name='Соус Чили',
            name_ru='Соус Чили',
            package='235 гр.',
            package_ru='235 гр.',
            description='Острый соус для блюд.',
            description_ru='Острый соус для блюд.',
            image=_tiny_png(),
        )
        self.product.extra_filters.add(self.filter)

    def test_active_product_page(self):
        url = reverse('product_detail', args=[self.product.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Соус Чили')
        self.assertContains(response, 'Sen Soy')
        self.assertContains(response, '235 гр.')
        self.assertContains(response, 'Без глютена')
        self.assertContains(response, 'Острый соус для блюд.')
        self.assertContains(response, 'class="pdp__media"')
        self.assertContains(response, f'href="{reverse("products")}"')

    def test_pdp_fills_brand_filters_when_empty(self):
        self.product.extra_filters.clear()
        response = self.client.get(
            reverse('product_detail', args=[self.product.slug])
        )
        self.assertContains(response, 'class="pdp__check"')
        self.assertContains(response, 'Натуральный продукт')

    def test_inactive_product_404(self):
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])
        response = self.client.get(
            reverse('product_detail', args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_unknown_slug_404(self):
        response = self.client.get(reverse('product_detail', args=['missing']))
        self.assertEqual(response.status_code, 404)

    def test_catalog_links_to_detail(self):
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        detail = reverse('product_detail', args=[self.product.slug])
        self.assertContains(response, f'href="{detail}"')

    def test_json_ld_product(self):
        import json
        from html import unescape
        import re

        html = self.client.get(
            reverse('product_detail', args=[self.product.slug])
        ).content.decode()
        match = re.search(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        data = json.loads(unescape(match.group(1)))
        types = {node['@type'] for node in data['@graph']}
        self.assertIn('Product', types)
        self.assertIn('BreadcrumbList', types)
        dumped = json.dumps(data)
        self.assertNotIn('AggregateRating', dumped)
        self.assertNotIn('Offer', dumped)


class CatalogSubcategoryChipTests(TestCase):
    def setUp(self):
        SiteSettings.load()
        self.snacks = Category.objects.create(slug='snacks', name='Снеки', order=10)
        self.chips = Category.objects.create(
            slug='chips', name='Чипсы', parent=self.snacks, order=0
        )
        self.bruschetta = Category.objects.create(
            slug='bruschetta', name='Брускетта', parent=self.snacks, order=1
        )
        self.crush = Category.objects.create(
            slug='crush', name='Краш', parent=self.snacks, order=2
        )
        self.brand = Brand.objects.create(
            slug='sen-soy',
            name='Sen Soy',
            logo=_tiny_png(),
        )
        self.chip_product = Product.objects.create(
            brand=self.brand,
            category=self.chips,
            slug='nori-chips',
            name='Чипсы нори',
            name_ru='Чипсы нори',
            package='4,5 гр.',
            image=_tiny_png(),
        )
        self.crush_product = Product.objects.create(
            brand=self.brand,
            category=self.crush,
            slug='pretzel-crush',
            name='Pretzel Crush',
            name_ru='Pretzel Crush',
            package='65 гр.',
            image=_tiny_png(),
        )
        self.family = [self.snacks]

    def test_toggle_child_replaces_parent(self):
        self.assertEqual(
            toggle_category_selection(
                ['snacks'], 'chips', categories=self.family
            ),
            ['chips'],
        )
        self.assertEqual(
            toggle_category_selection(
                ['chips'], 'bruschetta', categories=self.family
            ),
            ['bruschetta'],
        )
        self.assertEqual(
            toggle_category_selection(
                ['chips'], 'chips', categories=self.family
            ),
            ['snacks'],
        )

    def test_snacks_page_child_chip_drops_parent(self):
        html = self.client.get(
            reverse('products'), {'category': 'snacks'}
        ).content.decode()
        self.assertIn('category=chips', html)
        self.assertNotIn('category=snacks&amp;category=chips', html)
        self.assertNotIn('category=snacks&category=chips', html)

    def test_child_chip_filters_products(self):
        response = self.client.get(reverse('products'), {'category': 'chips'})
        self.assertContains(response, 'Чипсы нори')
        self.assertNotContains(response, 'Pretzel Crush')
        html = response.content.decode()
        self.assertRegex(html, r'chip--sub is-active[^>]*>Чипсы')
        self.assertIn('category=snacks', html)


class CatalogSnackBadgeTests(TestCase):
    def setUp(self):
        SiteSettings.load()
        self.snacks = Category.objects.create(slug='snacks', name='Снеки', order=10)
        self.chips = Category.objects.create(
            slug='chips', name='Чипсы', parent=self.snacks, order=0
        )
        self.riceup = Brand.objects.create(
            slug='riceup',
            name='RICEUP',
            logo=_tiny_png(),
        )

    def test_riceup_splits_chips_and_tortilla_badges(self):
        Product.objects.create(
            brand=self.riceup,
            category=self.chips,
            slug='riceup-rice-chips-sea-salt-60',
            name='Rice chips',
            name_ru='Рисовые чипсы',
            package='60 гр.',
            image=_tiny_png(),
        )
        Product.objects.create(
            brand=self.riceup,
            category=self.chips,
            slug='riceup-tortilla-chips-salt-60',
            name='Tortilla chips',
            name_ru='Тортилья-чипсы',
            package='60 гр.',
            image=_tiny_png(),
        )
        ensure_product_filters()
        ensure_product_filter_assignments()
        html = self.client.get(
            reverse('products'), {'category': 'snacks'}
        ).content.decode()
        self.assertIn('RICEUP', html)
        self.assertIn('Чипсы', html)
        self.assertIn('Тортильи', html)
        self.assertIn('popped-never-fried', html)
        self.assertIn('less-fat-60', html)
        self.assertIn('product-group__badge', html)
        self.assertNotIn('id="catalog-brand"', html)
