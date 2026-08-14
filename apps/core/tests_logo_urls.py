from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.core.templatetags.ajeres_tags import brand_logo_url, partner_logo_url


class LogoUrlTests(SimpleTestCase):
    def test_brand_uses_static_path(self):
        url = brand_logo_url(SimpleNamespace(slug='paprichi', logo=None))
        self.assertIn('img/brands/paprichi.jpg', url)

    def test_partner_uses_static_path(self):
        url = partner_logo_url(SimpleNamespace(slug='makro', logo=None))
        self.assertIn('img/partners/makro.png', url)
