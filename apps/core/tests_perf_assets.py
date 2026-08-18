from django.test import TestCase
from django.urls import reverse

from apps.core.models import CompanyStat


class HomepagePerfAssetsTests(TestCase):
    def setUp(self):
        CompanyStat.objects.create(value='7+', label='лет', order=0, is_active=True)
        self.response = self.client.get(reverse('home'))
        self.html = self.response.content.decode()

    def test_home_ok(self):
        self.assertEqual(self.response.status_code, 200)

    def test_no_google_fonts(self):
        self.assertNotIn('fonts.googleapis.com', self.html)
        self.assertNotIn('fonts.gstatic.com', self.html)
        self.assertIn('fonts/comfortaa-700-cyrillic.woff2', self.html)
        self.assertIn('css/fonts.css', self.html)

    def test_hero_static_webp_preloaded_not_lazy(self):
        self.assertIn('img/hero-samarkand.webp', self.html)
        self.assertIn('img/hero-samarkand-640.webp', self.html)
        self.assertIn('rel="preload"', self.html)
        self.assertIn('as="image"', self.html)
        self.assertNotIn('hero-samarkand.png', self.html)
        hero_start = self.html.find('class="home-hero__img"')
        hero_tag = self.html[hero_start : hero_start + 700]
        self.assertNotIn('loading="lazy"', hero_tag)
        self.assertIn('fetchpriority="high"', hero_tag)

    def test_footer_skyline_is_lazy_webp(self):
        self.assertIn('footer-samarkand-silhouette-1440.webp', self.html)
        self.assertIn('footer-samarkand-silhouette-800.webp', self.html)
        sky_start = self.html.find('class="site-footer__skyline-img"')
        sky_tag = self.html[sky_start : sky_start + 700]
        self.assertIn('loading="lazy"', sky_tag)
        self.assertIn('fetchpriority="low"', sky_tag)
        self.assertNotIn('footer-samarkand-silhouette.png', self.html)

    def test_logo_and_fingerprint_webp(self):
        self.assertIn('img/logo-ajeres.webp', self.html)
        self.assertIn('img/fingerprint-white.webp', self.html)

    def test_deferred_css_only_below_fold(self):
        deferred = {
            'css/footer.css',
            'css/footer-2.css',
            'css/contact-modal.css',
            'css/breadcrumbs.css',
            'css/home-2.css',
            'css/home-3.css',
        }
        blocking = {
            'css/fonts.css',
            'css/base.css',
            'css/layout.css',
            'css/nav-mobile.css',
            'css/pages.css',
            'css/home.css',
            'css/home-stats.css',
        }
        for href in deferred:
            marker = f'href="/static/{href}"'
            idx = self.html.find(marker)
            self.assertGreater(idx, -1, href)
            window = self.html[max(0, idx - 80) : idx + len(marker) + 40]
            self.assertIn('data-defer-css', window)
            self.assertIn('media="print"', window)
        for href in blocking:
            marker = f'href="/static/{href}"'
            idx = self.html.find(marker)
            self.assertGreater(idx, -1, href)
            window = self.html[max(0, idx - 80) : idx + len(marker) + 40]
            self.assertNotIn('data-defer-css', window)

    def test_nav_mobile_css_is_max_959_media(self):
        marker = 'href="/static/css/nav-mobile.css"'
        idx = self.html.find(marker)
        self.assertGreater(idx, -1)
        window = self.html[max(0, idx - 80) : idx + len(marker) + 50]
        self.assertNotIn('data-defer-css', window)
        self.assertIn('media="(max-width: 959px)"', window)
