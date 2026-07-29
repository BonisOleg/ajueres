from django.test import TestCase

from apps.core.models import SiteBlock
from apps.core.selectors import get_blocks, get_site_settings, is_section_visible


class CoreSelectorsTests(TestCase):
    def test_site_settings_singleton(self):
        a = get_site_settings()
        b = get_site_settings()
        self.assertEqual(a.pk, 1)
        self.assertEqual(b.pk, 1)

    def test_blocks_and_visibility(self):
        SiteBlock.objects.create(page='home', key='hero_visible', text_html='1')
        SiteBlock.objects.create(page='home', key='brands_visible', text_html='0')
        blocks = get_blocks('home')
        self.assertTrue(is_section_visible(blocks, 'hero_visible'))
        self.assertFalse(is_section_visible(blocks, 'brands_visible'))
        self.assertFalse(is_section_visible(blocks, 'missing_visible'))
