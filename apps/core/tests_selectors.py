from django.core.cache import cache
from django.test import TestCase
from django.utils.translation import override

from apps.core.models import SiteBlock
from apps.core.selectors import get_block_text, get_blocks, get_site_settings, is_section_visible


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

    def test_contacts_blocks_translate_when_uz_en_empty(self):
        cache.clear()
        SiteBlock.objects.create(
            page='contacts',
            key='map_title',
            text_html='Наш офис в Ташкенте',
            text_html_ru='Наш офис в Ташкенте',
            text_html_uz='',
            text_html_en='',
        )
        SiteBlock.objects.create(
            page='contacts',
            key='form_title',
            text_html='Отправить нам запрос',
            text_html_ru='Отправить нам запрос',
        )
        SiteBlock.objects.create(
            page='contacts',
            key='intro',
            text_html=(
                'Команда ООО «AJERES» всегда открыта для новых партнерств и '
                'готова обсудить возможности сотрудничества.'
            ),
            text_html_ru=(
                'Команда ООО «AJERES» всегда открыта для новых партнерств и '
                'готова обсудить возможности сотрудничества.'
            ),
        )
        with override('en'):
            blocks = get_blocks('contacts')
            self.assertEqual(
                get_block_text(blocks, 'map_title'),
                'Our office in Tashkent',
            )
            self.assertEqual(
                get_block_text(blocks, 'form_title'),
                'Send us a request',
            )
            self.assertIn(
                'always open to new partnerships',
                get_block_text(blocks, 'intro'),
            )
        with override('uz'):
            blocks = get_blocks('contacts')
            self.assertEqual(
                get_block_text(blocks, 'map_title'),
                'Toshkentdagi ofisimiz',
            )
            self.assertEqual(
                get_block_text(blocks, 'form_title'),
                'Bizga so‘rov yuboring',
            )
            self.assertIn('hamkorliklar uchun ochiq', get_block_text(blocks, 'intro'))
        with override('ru'):
            blocks = get_blocks('contacts')
            self.assertEqual(
                get_block_text(blocks, 'map_title'),
                'Наш офис в Ташкенте',
            )

    def test_contacts_block_keeps_custom_translation(self):
        cache.clear()
        SiteBlock.objects.create(
            page='contacts',
            key='map_title',
            text_html='Наш офис в Ташкенте',
            text_html_ru='Наш офис в Ташкенте',
            text_html_en='Tashkent HQ',
        )
        with override('en'):
            blocks = get_blocks('contacts')
            self.assertEqual(get_block_text(blocks, 'map_title'), 'Tashkent HQ')
