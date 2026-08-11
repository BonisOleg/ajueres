from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models

from .theme_fields import (
    DEFAULT_ACCENT,
    DEFAULT_ACCENT_INK,
    DEFAULT_ACCENT_SOFT,
    validate_hex_color,
)
from .theme_models import BlockStyle, SiteButtonStyle  # noqa: F401


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """Singleton глобальних налаштувань сайту (pk=1)."""

    company_name = models.CharField('Назва компанії', max_length=255, default='AJERES')
    phone = models.CharField('Телефон', max_length=64, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.TextField('Адреса', blank=True)

    accent_color = models.CharField(
        'Акцентний колір',
        max_length=7,
        default=DEFAULT_ACCENT,
        help_text='Hex, напр. #FF5A36',
    )
    accent_ink = models.CharField(
        'Акцент (темніший / hover)',
        max_length=7,
        default=DEFAULT_ACCENT_INK,
        help_text='Hex',
    )
    accent_soft = models.CharField(
        'Акцент (мʼякий фон)',
        max_length=7,
        default=DEFAULT_ACCENT_SOFT,
        help_text='Hex',
    )

    class Meta:
        verbose_name = 'Налаштування сайту'
        verbose_name_plural = 'Налаштування сайту'

    def __str__(self):
        return self.company_name or 'SiteSettings'

    def clean(self):
        super().clean()
        errors = {}
        for field in ('accent_color', 'accent_ink', 'accent_soft'):
            try:
                validate_hex_color(getattr(self, field), allow_blank=False)
            except ValidationError as exc:
                errors[field] = exc
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.pk = 1
        self.full_clean()
        super().save(*args, **kwargs)
        cache.delete('site_settings')

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    get_solo = load


class SiteBlock(models.Model):
    """CMS-блок: унікальна пара (page, key) — тексти/фото/visibility секцій."""

    page = models.CharField('Сторінка', max_length=64, db_index=True)
    key = models.CharField('Ключ', max_length=128)
    text_html = models.TextField('Текст / HTML / visibility', blank=True, default='')
    image = models.ImageField('Зображення', upload_to='cms/blocks/', blank=True, null=True)

    class Meta:
        verbose_name = 'CMS-блок'
        verbose_name_plural = 'CMS-блоки'
        constraints = [
            models.UniqueConstraint(fields=['page', 'key'], name='uniq_siteblock_page_key'),
        ]
        ordering = ['page', 'key']

    def __str__(self):
        return f'{self.page}.{self.key}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from .selectors import invalidate_site_blocks_cache

        invalidate_site_blocks_cache(self.page)


class LegalDocument(TimeStampedModel):
    """Правові документи. За картою — лише політика приватності."""

    slug = models.SlugField('Slug', max_length=64, unique=True)
    title = models.CharField('Заголовок', max_length=255)
    body = models.TextField('Текст', blank=True)

    class Meta:
        verbose_name = 'Правовий документ'
        verbose_name_plural = 'Правові документи'
        ordering = ['slug']

    def __str__(self):
        return self.title


class Advantage(TimeStampedModel):
    """Переваги на головній."""

    icon_key = models.CharField(
        'Ключ іконки',
        max_length=64,
        blank=True,
        help_text='Ідентифікатор іконки у фронтенді',
    )
    title = models.CharField('Заголовок', max_length=255)
    text = models.TextField('Опис', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Перевага'
        verbose_name_plural = 'Переваги'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class CompanyStat(TimeStampedModel):
    """Цифри компанії (200+ партнерів тощо)."""

    value = models.CharField('Значення', max_length=64)
    label = models.CharField('Підпис', max_length=255)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Цифра'
        verbose_name_plural = 'Цифри'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.value} — {self.label}'


class AboutSection(TimeStampedModel):
    """Секції сторінки «Про компанію»."""

    section_key = models.SlugField(
        'Ключ секції',
        max_length=64,
        unique=True,
        help_text='history, mission, vision, values, market…',
    )
    title = models.CharField('Заголовок', max_length=255)
    body = models.TextField('Текст', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Секція «Про компанію»'
        verbose_name_plural = 'Секції «Про компанію»'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.section_key}: {self.title}'


class PartnerOffer(TimeStampedModel):
    """Пропозиції для партнерів на /contacts (окремої /partners немає)."""

    title = models.CharField('Заголовок', max_length=255)
    text = models.TextField('Опис', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Пропозиція для партнерів'
        verbose_name_plural = 'Пропозиції для партнерів'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class RetailPartner(TimeStampedModel):
    """Покупець / ритейл-партнер — логотипи в блоці «Наши бренды» на головній."""

    slug = models.SlugField('Slug', max_length=64, unique=True)
    name = models.CharField('Назва', max_length=255)
    logo = models.ImageField(
        'Логотип',
        upload_to='core/retail_partners/',
        blank=True,
        null=True,
    )
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Покупець (ритейл)'
        verbose_name_plural = 'Покупці (ритейл)'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from .selectors import invalidate_retail_partners_cache

        invalidate_retail_partners_cache()

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        from .selectors import invalidate_retail_partners_cache

        invalidate_retail_partners_cache()
        return result


class CaseStudy(TimeStampedModel):
    """Опційні кейси / історії успіху на головній."""

    title = models.CharField('Заголовок', max_length=255)
    text = models.TextField('Текст', blank=True)
    metric = models.CharField('Метрика', max_length=128, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейси'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


# CMS proxy slots (must be imported with the model graph for migrations/admin).
from .cms_proxy_models import SECTION_PROXY_MODELS as _SECTION_PROXY_MODELS  # noqa: E402,F401
