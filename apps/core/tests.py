from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.core.views import _about_presentation


class AboutPresentationTests(SimpleTestCase):
    def test_structures_market_copy_without_losing_content(self):
        market = SimpleNamespace(
            section_key='market',
            body=(
                'Головна теза.\n\n'
                'Основные преимущества рынка:\n'
                '• перший факт;\n'
                '• другий факт.\n\n'
                'Підсумковий текст.'
            ),
        )

        result = _about_presentation([market])

        self.assertEqual(result['market_intro'], 'Головна теза.')
        self.assertEqual(
            result['market_label'],
            'Основные преимущества рынка:',
        )
        self.assertEqual(
            result['market_facts'],
            ['перший факт;', 'другий факт.'],
        )
        self.assertEqual(result['market_outro'], ['Підсумковий текст.'])
