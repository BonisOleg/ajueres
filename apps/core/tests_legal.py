from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.core.legal_defaults import (
    OFFER_DEFAULTS,
    PRIVACY_DEFAULTS,
    ensure_legal_document,
)
from apps.core.models import LegalDocument


class LegalPagesTests(TestCase):
    def setUp(self):
        ensure_legal_document('privacy', PRIVACY_DEFAULTS)
        ensure_legal_document('offer', OFFER_DEFAULTS)

    def test_privacy_and_offer_pages(self):
        privacy = self.client.get(reverse('privacy'))
        offer = self.client.get(reverse('offer'))
        self.assertEqual(privacy.status_code, 200)
        self.assertEqual(offer.status_code, 200)
        self.assertContains(privacy, 'Политика конфиденциальности')
        self.assertContains(offer, 'Публичная оферта')
        self.assertContains(offer, 'Реквизиты')
        self.assertContains(offer, 'ИНН:')

    def test_unknown_slug_404(self):
        LegalDocument.objects.create(
            slug='other',
            title='Other',
            body='Text',
        )
        response = self.client.get('/legal/other/')
        self.assertEqual(response.status_code, 404)

    def test_empty_body_is_refilled(self):
        LegalDocument.objects.filter(slug='privacy').update(
            body='',
            body_ru='',
            body_uz='',
            body_en='',
        )
        response = self.client.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Политика конфиденциальности')

    def test_default_language_legal_urls(self):
        privacy = self.client.get('/privacy/')
        offer = self.client.get('/offer/')
        self.assertEqual(privacy.status_code, 200)
        self.assertEqual(offer.status_code, 200)

    def test_ru_prefix_redirects_to_unprefixed(self):
        response = self.client.get('/ru/privacy/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/privacy/')

    def test_home_has_legal_links(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, reverse('privacy'))
        self.assertContains(response, reverse('offer'))

    def test_seed_does_not_overwrite(self):
        doc = LegalDocument.objects.get(slug='privacy')
        doc.body = 'Custom editor text'
        doc.body_ru = 'Custom editor text'
        doc.save()
        ensure_legal_document('privacy', PRIVACY_DEFAULTS)
        doc.refresh_from_db()
        self.assertEqual(doc.body, 'Custom editor text')

    def test_ensure_legal_command(self):
        LegalDocument.objects.all().delete()
        call_command('ensure_legal')
        slugs = set(LegalDocument.objects.values_list('slug', flat=True))
        self.assertIn('privacy', slugs)
        self.assertIn('offer', slugs)
        from apps.core.models import RetailPartner

        self.assertTrue(RetailPartner.objects.filter(slug='korzinka').exists())

    def test_seed_creates_both(self):
        LegalDocument.objects.all().delete()
        call_command('seed_site')
        slugs = set(LegalDocument.objects.values_list('slug', flat=True))
        self.assertIn('privacy', slugs)
        self.assertIn('offer', slugs)
