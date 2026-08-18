from django.test import TestCase
from django.urls import reverse


CREDIT_URL = 'https://www.prometeylabs.com/corporate-website-v2/'


class FooterDeveloperLinkTests(TestCase):
    def test_home_has_nofollow_credit_link(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, CREDIT_URL)
        self.assertContains(response, 'rel="nofollow noopener noreferrer"')
        self.assertContains(response, '>PrometeyLabs</a>')

    def test_localized_home_keeps_credit_link(self):
        for path in ('/en/', '/uz/'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, CREDIT_URL)
                self.assertContains(response, 'nofollow')

    def test_inner_pages_show_credit_without_link(self):
        urls = (reverse('about'), reverse('products'), reverse('contacts'))
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'PrometeyLabs')
                self.assertNotContains(response, CREDIT_URL)
                self.assertNotContains(response, 'site-footer__credit-link')
                self.assertContains(response, 'site-footer__credit-name')
