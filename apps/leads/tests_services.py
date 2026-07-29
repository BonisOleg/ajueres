from django.test import TestCase, override_settings

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
