"""Persist media blobs in the database (Vercel /tmp is ephemeral)."""

from __future__ import annotations

from django.db import models


class MediaBlob(models.Model):
    """Durable copy of an uploaded media file for serverless deploys."""

    path = models.CharField('Путь', max_length=500, unique=True, db_index=True)
    data = models.BinaryField('Данные')
    content_type = models.CharField(
        'Content-Type',
        max_length=128,
        default='application/octet-stream',
    )
    size = models.PositiveIntegerField('Размер', default=0)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Медиафайл (БД)'
        verbose_name_plural = 'Медиафайлы (БД)'

    def __str__(self) -> str:
        return self.path
