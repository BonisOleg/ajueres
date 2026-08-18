from django.test import SimpleTestCase

from apps.core.requisites import normalize_requisites, parse_requisites_text


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
