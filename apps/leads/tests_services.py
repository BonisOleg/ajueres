from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import translation

from apps.leads.models import ContactInquiry
from apps.leads.services import RateLimitExceeded, submit_contact_inquiry


class LeadsServicesTests(TestCase):
    def test_submit_ok(self):
        result = submit_contact_inquiry(
            purpose='Хочу партнерство',
            name='Иван',
            phone='+998 90 123-45-67',
            email='ivan@example.com',
            ip_address='127.0.0.1',
            language='ru',
        )
        self.assertIsNotNone(result.inquiry)
        self.assertFalse(result.skipped_honeypot)
        self.assertEqual(result.inquiry.phone, '+998 (90) 123-45-67')

    def test_honeypot_skips_db(self):
        result = submit_contact_inquiry(
            purpose='Хочу партнерство',
            name='Иван',
            phone='+998901234567',
            email='ivan@example.com',
            honeypot='bot',
            ip_address='10.0.0.1',
        )
        self.assertTrue(result.skipped_honeypot)
        self.assertIsNone(result.inquiry)

    def test_purpose_min_length(self):
        with self.assertRaises(ValidationError) as ctx:
            submit_contact_inquiry(
                purpose='abcd',
                name='Иван',
                phone='+998 (90) 123-45-67',
                email='ivan@example.com',
            )
        self.assertIn('purpose', ctx.exception.message_dict)

    def test_name_rejects_digits(self):
        with self.assertRaises(ValidationError) as ctx:
            submit_contact_inquiry(
                purpose='Нужен прайс-лист',
                name='Иван2',
                phone='+998 (90) 123-45-67',
                email='ivan@example.com',
            )
        self.assertIn('name', ctx.exception.message_dict)

    def test_name_allows_apostrophe_and_strips_zwsp(self):
        result = submit_contact_inquiry(
            purpose='Нужен прайс-лист',
            name="О\u200b'Коннор",
            phone='+998 (90) 123-45-67',
            email='okonnor@example.com',
        )
        self.assertIsNotNone(result.inquiry)
        self.assertEqual(result.inquiry.name, "О'Коннор")

    def test_phone_requires_twelve_digits(self):
        with self.assertRaises(ValidationError) as ctx:
            submit_contact_inquiry(
                purpose='Нужен прайс-лист',
                name='Иван',
                phone='+998 (90) 123-45',
                email='ivan@example.com',
            )
        self.assertIn('phone', ctx.exception.message_dict)

    def test_email_requires_domain_zone(self):
        with self.assertRaises(ValidationError) as ctx:
            submit_contact_inquiry(
                purpose='Нужен прайс-лист',
                name='Иван',
                phone='+998 (90) 123-45-67',
                email='ivan@company',
            )
        self.assertIn('email', ctx.exception.message_dict)

    def test_error_messages_russian(self):
        with translation.override('ru'):
            with self.assertRaises(ValidationError) as ctx:
                submit_contact_inquiry(
                    purpose='ab',
                    name='1',
                    phone='123',
                    email='bad',
                )
            messages = {
                field: errs[0] for field, errs in ctx.exception.message_dict.items()
            }
            self.assertEqual(
                messages['purpose'],
                'Укажите цель обращения (минимум 5 символов).',
            )
            self.assertEqual(
                messages['name'],
                'Имя должно содержать только буквы и быть не короче 2 символов.',
            )
            self.assertEqual(
                messages['phone'],
                'Введите корректный номер телефона в формате +998 (XX) XXX-XX-XX.',
            )
            self.assertEqual(
                messages['email'],
                'Введите корректный адрес электронной почты.',
            )

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'leads-test',
            }
        }
    )
    def test_rate_limit(self):
        kwargs = dict(
            purpose='Хочу партнерство',
            name='Иван',
            phone='+998901234567',
            email='ivan@example.com',
            ip_address='203.0.113.10',
        )
        for _ in range(5):
            submit_contact_inquiry(**kwargs)
        with self.assertRaises(RateLimitExceeded):
            submit_contact_inquiry(**kwargs)
        self.assertEqual(ContactInquiry.objects.filter(ip_address='203.0.113.10').count(), 5)
