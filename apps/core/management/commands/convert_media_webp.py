"""Convert existing ImageField media files to WebP and update DB paths."""

from __future__ import annotations

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models

from apps.core.image_webp import convert_stored_image


class Command(BaseCommand):
    help = 'Convert already uploaded ImageField files in media to WebP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without writing files or DB',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        converted = 0
        skipped = 0

        for model in apps.get_models():
            image_fields = [
                field
                for field in model._meta.fields
                if isinstance(field, models.ImageField)
            ]
            if not image_fields:
                continue
            for obj in model.objects.all().iterator():
                updates = []
                for field in image_fields:
                    file_field = getattr(obj, field.name)
                    old_name = getattr(file_field, 'name', '') or ''
                    if not old_name:
                        continue
                    new_name = convert_stored_image(
                        file_field.storage,
                        old_name,
                        write=not dry_run,
                    )
                    if not new_name or new_name == old_name:
                        skipped += 1
                        continue
                    verb = 'would convert' if dry_run else 'converted'
                    self.stdout.write(
                        f'  {verb} {model._meta.label}.{field.name}: '
                        f'{old_name} → {new_name}'
                    )
                    converted += 1
                    if dry_run:
                        continue
                    setattr(obj, field.attname, new_name)
                    updates.append(field.name)
                    if file_field.storage.exists(old_name):
                        file_field.storage.delete(old_name)
                if updates:
                    obj.save(update_fields=updates)

        self.stdout.write(
            self.style.SUCCESS(
                f'converted={converted}, skipped={skipped}, dry_run={dry_run}'
            )
        )
