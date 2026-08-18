from django.test import SimpleTestCase

from apps.core.requisites import (
    display_requisites_rows,
    normalize_requisites,
    parse_requisites_text,
)


class RequisitesParseTests(SimpleTestCase):
    def test_parse_label_value_lines(self):
        rows = parse_requisites_text('ИНН:\nр/с: 111\nБанк:\nАдрес:')
        self.assertEqual(
            rows,
            [
                {'label': 'ИНН', 'value': ''},
                {'label': 'р/с', 'value': '111'},
                {'label': 'Банк', 'value': ''},
                {'label': 'Адрес', 'value': ''},
            ],
        )

    def test_normalize_drops_empty_rows(self):
        rows = normalize_requisites(
            [
                {'label': 'ИНН', 'value': '1'},
                {'label': '  ', 'value': ''},
                {'label': 'Банк', 'value': ''},
            ]
        )
        self.assertEqual(
            rows,
            [
                {'label': 'ИНН', 'value': '1'},
                {'label': 'Банк', 'value': ''},
            ],
        )

    def test_normalize_json_string(self):
        rows = normalize_requisites('[{"label": "TIN", "value": "9"}]')
        self.assertEqual(rows, [{'label': 'TIN', 'value': '9'}])

    def test_display_always_has_four_standard_fields(self):
        rows = display_requisites_rows([], 'ru')
        self.assertEqual(
            [row['label'] for row in rows],
            ['ИНН', 'р/с', 'Банк', 'Адрес'],
        )
        filled = display_requisites_rows([{'label': 'ИНН', 'value': '99'}], 'ru')
        self.assertEqual(filled[0], {'label': 'ИНН', 'value': '99'})
        self.assertEqual(filled[1]['label'], 'р/с')
