from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """Категорія каталогу (соуси, макаронні, нори, сиропи, чипси)."""

    slug = models.SlugField('Slug', max_length=64, unique=True)
    name = models.CharField('Назва', max_length=255)
    image = models.ImageField(
        'Зображення',
        upload_to='catalog/categories/',
        blank=True,
        null=True,
    )
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Brand(TimeStampedModel):
    """Бренд = виробник. Блок під каталогом на /products."""

    slug = models.SlugField('Slug', max_length=64, unique=True)
    name = models.CharField('Назва', max_length=255)
    logo = models.ImageField(
        'Логотип',
        upload_to='catalog/brands/',
        blank=True,
        null=True,
    )
    short_description = models.TextField('Короткий опис', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)
    is_featured = models.BooleanField(
        'Під каталогом',
        default=True,
        help_text='Показувати в блоці виробників під каталогом на /products',
    )

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренди'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from .selectors import invalidate_catalog_list_cache

        invalidate_catalog_list_cache()

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        from .selectors import invalidate_catalog_list_cache

        invalidate_catalog_list_cache()
        return result


class Product(TimeStampedModel):
    """
    Товар як на https://ajeres.uz/catalog.html —
    картка: фото, назва, фасування; завжди рівно один бренд.
    """

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Бренд',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Категорія',
    )
    slug = models.SlugField('Slug', max_length=128, unique=True)
    name = models.CharField(
        'Назва',
        max_length=255,
        help_text='Без дубля бренду, напр. Соус «Сладкий Чили»',
    )
    package = models.CharField(
        'Фасування',
        max_length=64,
        help_text='Напр. 235 гр., 1 л., 4,5 гр.',
    )
    description = models.TextField('Опис', blank=True)
    image = models.ImageField(
        'Фото',
        upload_to='catalog/products/',
        blank=True,
        null=True,
    )
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['brand__order', 'order', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
        ]

    def __str__(self):
        return f'{self.brand.name} — {self.name} ({self.package})'
