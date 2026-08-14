from django.db import migrations


def seed_legal_documents(apps, schema_editor):
    from apps.core.legal_defaults import (
        OFFER_DEFAULTS,
        PRIVACY_DEFAULTS,
        ensure_legal_document,
    )

    ensure_legal_document('privacy', PRIVACY_DEFAULTS)
    ensure_legal_document('offer', OFFER_DEFAULTS)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_legal_document_requisites'),
    ]

    operations = [
        migrations.RunPython(seed_legal_documents, migrations.RunPython.noop),
    ]
