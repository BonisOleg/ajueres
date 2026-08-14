import json
import re
from html import unescape

from django.conf import settings
from django.test import TestCase, override_settings

from apps.core.legal_defaults import OFFER_DEFAULTS, PRIVACY_DEFAULTS, ensure_legal_document
from apps.core.models import SiteSettings
from apps.core.seo import admin_disallow_path, public_site_url

PUBLIC = 'https://ajeres.uz'


def _json_ld(html: str) -> dict:
    match = re.search(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    assert match, 'JSON-LD script missing'
    return json.loads(unescape(match.group(1)))


@override_settings(PUBLIC_SITE_URL=PUBLIC)
class SeoTests(TestCase):
    def setUp(self):
        SiteSettings.load()
        ensure_legal_document('privacy', PRIVACY_DEFAULTS)
        ensure_legal_document('offer', OFFER_DEFAULTS)

    def test_canonical_strips_catalog_query(self):
        response = self.client.get('/products/?category=sauces&page=2')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{PUBLIC}/products/"')
        self.assertContains(response, 'rel="canonical"')
        self.assertNotContains(response, f'canonical" href="{PUBLIC}/products/?')

    def test_noindex_only_with_filter_query(self):
        clean = self.client.get('/products/')
        self.assertEqual(clean.status_code, 200)
        self.assertNotContains(clean, 'name="robots"')
        filtered = self.client.get('/products/?category=sauces')
        self.assertContains(filtered, 'name="robots" content="noindex, follow"')

    def test_hreflang_pairs_and_no_ru_prefix(self):
        response = self.client.get('/about/')
        html = response.content.decode()
        self.assertIn(f'hreflang="ru" href="{PUBLIC}/about/"', html)
        self.assertIn(f'hreflang="uz" href="{PUBLIC}/uz/about/"', html)
        self.assertIn(f'hreflang="en" href="{PUBLIC}/en/about/"', html)
        self.assertIn(f'hreflang="x-default" href="{PUBLIC}/about/"', html)
        self.assertNotIn(f'{PUBLIC}/ru/', html)

    def test_uz_canonical_keeps_prefix(self):
        response = self.client.get('/uz/contacts/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'rel="canonical" href="{PUBLIC}/uz/contacts/"')

    def test_sitemap_languages_no_query_no_admin(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        locs = re.findall(r'<loc>(.*?)</loc>', body)
        for loc in locs:
            self.assertNotIn('?', loc)
            self.assertNotIn(admin_disallow_path(), loc)
        self.assertIn(f'{PUBLIC}/</loc>', body)
        self.assertIn(f'{PUBLIC}/uz/</loc>', body)
        self.assertIn(f'{PUBLIC}/en/products/</loc>', body)
        self.assertIn(f'{PUBLIC}/privacy/</loc>', body)
        locs = re.findall(r'<loc>(.*?)</loc>', body)
        self.assertEqual(len(locs), len(settings.LANGUAGES) * 6)

    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        text = response.content.decode()
        self.assertIn(f'Sitemap: {PUBLIC}/sitemap.xml', text)
        self.assertIn(f'Disallow: {admin_disallow_path()}', text)
        self.assertIn('Disallow: /i18n/', text)
        self.assertNotIn('Disallow: /products/', text)

    def test_json_ld_org_no_forbidden_types(self):
        home = _json_ld(self.client.get('/').content.decode())
        types = {node['@type'] for node in home['@graph']}
        self.assertIn('Organization', types)
        self.assertIn('WebSite', types)
        self.assertNotIn('LocalBusiness', types)
        dumped = json.dumps(home)
        self.assertNotIn('AggregateRating', dumped)
        self.assertNotIn('SearchAction', dumped)
        self.assertTrue(any(n.get('@id') == f'{PUBLIC}#org' for n in home['@graph']))

        contacts = _json_ld(self.client.get('/contacts/').content.decode())
        ctypes = {node['@type'] for node in contacts['@graph']}
        self.assertIn('LocalBusiness', ctypes)
        self.assertIn('BreadcrumbList', ctypes)
        self.assertNotIn('WebSite', ctypes)

        home_bc = {node['@type'] for node in home['@graph']}
        self.assertNotIn('BreadcrumbList', home_bc)

    def test_unique_titles_and_descriptions(self):
        paths = ['/', '/products/', '/about/', '/contacts/', '/privacy/', '/offer/']
        titles = []
        descriptions = []
        for path in paths:
            html = self.client.get(path).content.decode()
            title = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
            desc = re.search(
                r'<meta name="description" content="([^"]+)"',
                html,
            )
            self.assertIsNotNone(title, path)
            self.assertIsNotNone(desc, path)
            titles.append(title.group(1).strip())
            descriptions.append(desc.group(1).strip())
            og_title = re.search(r'property="og:title" content="([^"]+)"', html)
            self.assertEqual(title.group(1).strip(), og_title.group(1).strip())
        self.assertEqual(len(titles), len(set(titles)))
        self.assertEqual(len(descriptions), len(set(descriptions)))

    def test_public_site_url_strips_www(self):
        with override_settings(PUBLIC_SITE_URL='https://www.ajeres.uz/'):
            self.assertEqual(public_site_url(), PUBLIC)

    def test_csp_excludes_admin_path(self):
        prefixes = tuple(settings.CONTENT_SECURITY_POLICY['EXCLUDE_URL_PREFIXES'])
        admin_login = f'{settings.ADMIN_PATH_PREFIX}/login/'
        self.assertTrue(admin_login.startswith(prefixes))
        self.assertFalse('/products/'.startswith(prefixes))
        for prefix in prefixes:
            self.assertFalse(prefix.startswith('//'))
