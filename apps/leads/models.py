from django.db import models


class ContactInquiry(models.Model):
    """Заявка з форми зворотного зв'язку (4 поля з карти сайту)."""

    class Status(models.TextChoices):
        NEW = 'new', 'Нова'
        PROCESSED = 'processed', 'Опрацьована'

    class Language(models.TextChoices):
        RU = 'ru', 'Русский'
        UZ = 'uz', "O'zbekcha"
        EN = 'en', 'English'

    purpose = models.TextField('Мета звернення')
    name = models.CharField("Ім'я", max_length=255)
    phone = models.CharField('Телефон', max_length=64)
    email = models.EmailField('Email')
    language = models.CharField(
        'Мова',
        max_length=8,
        choices=Language.choices,
        default=Language.RU,
    )
    status = models.CharField(
        'Статус',
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.email} ({self.created_at:%Y-%m-%d})'
