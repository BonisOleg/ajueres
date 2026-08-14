from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Brand, Category, Product, ProductFilter
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
