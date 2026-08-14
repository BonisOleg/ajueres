from django.core.management.base import BaseCommand

from apps.core.legal_defaults import (
    OFFER_DEFAULTS,
    PRIVACY_DEFAULTS,
    ensure_legal_document,
)


class Command(BaseCommand):
    help = 'Create privacy/offer legal pages if missing (safe for production).'

    def handle(self, *args, **options):
        _, privacy_created = ensure_legal_document('privacy', PRIVACY_DEFAULTS)
        _, offer_created = ensure_legal_document('offer', OFFER_DEFAULTS)
        self.stdout.write(
            f'privacy={"created" if privacy_created else "ok"}, '
            f'offer={"created" if offer_created else "ok"}'
        )
