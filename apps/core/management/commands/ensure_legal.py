from django.core.management.base import BaseCommand

from apps.core.ensure_showcase import ensure_showcase
from apps.core.legal_defaults import (
    OFFER_DEFAULTS,
    PRIVACY_DEFAULTS,
    ensure_legal_document,
)


class Command(BaseCommand):
    help = 'Create privacy/offer pages and partner/brand rows if missing.'

    def handle(self, *args, **options):
        _, privacy_created = ensure_legal_document('privacy', PRIVACY_DEFAULTS)
        _, offer_created = ensure_legal_document('offer', OFFER_DEFAULTS)
        ensure_showcase()
        self.stdout.write(
            f'privacy={"created" if privacy_created else "ok"}, '
            f'offer={"created" if offer_created else "ok"}, showcase=ok'
        )
