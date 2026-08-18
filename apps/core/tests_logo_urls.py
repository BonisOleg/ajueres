from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from apps.core.templatetags.ajeres_tags import brand_logo_url, partner_logo_url


class LogoUrlTests(SimpleTestCase):
    def test_brand_uses_static_path(self):
        url = brand_logo_url(SimpleNamespace(slug='paprichi', logo=None))
        self.assertIn('img/brands/paprichi.webp', url)

    def test_brand_matches_display_name(self):
        url = brand_logo_url(SimpleNamespace(slug='custom', name='ЯМЧАН', logo=None))
        self.assertIn('img/brands/yamchan.webp', url)

    def test_partner_uses_static_path(self):
        url = partner_logo_url(SimpleNamespace(slug='makro', logo=None))
        self.assertIn('img/partners/makro.webp', url)

    def test_partner_maps_media_filename(self):
        url = partner_logo_url(
            SimpleNamespace(
                slug='unknown-partner',
                logo=SimpleNamespace(name='core/retail_partners/uzum.png', url=''),
            )
        )
        self.assertIn('img/partners/uzum.webp', url)


class MediaLogoRedirectTests(TestCase):
    def test_partner_media_redirects_to_static(self):
        response = self.client.get('/media/core/retail_partners/korzinka.png')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/static/img/partners/korzinka.webp', response['Location'])

    def test_brand_media_redirects_to_static(self):
        response = self.client.get('/media/catalog/brands/paprichi.jpg')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/static/img/brands/paprichi.webp', response['Location'])
