from django.conf import settings
from django.db import models
from django.urls import reverse

from .search import build_search_text

_SEARCH_TRANSLATED_FIELDS = ('name', 'package', 'description')


def _search_languages() -> tuple[str, ...]:
    codes = getattr(settings, 'MODELTRANSLATION_LANGUAGES', None)
    if not codes:
        codes = [code for code, _ in getattr(settings, 'LANGUAGES', [])]
    return tuple(code.replace('-', '_') for code in codes)


def _translated_values(obj, base_fields: tuple[str, ...]):
    """Значення всіх мовних варіантів полів (name_ru, name_uz, …)."""
    if obj is None:
        return
    for base in base_fields:
        for lang in _search_languages():
            yield getattr(obj, f'{base}_{lang}', '') or ''


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """Категорія каталогу (соуси, лапша, водорості, рисова бумага, снеки…)."""

    slug = models.SlugField('Slug', max_length=64, unique=True)
    name = models.CharField('Название', max_length=255)
    parent = models.ForeignKey(
        'self',
        verbose_name='Родительская категория',
        related_name='children',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='catalog/categories/',
        blank=True,
        null=True,
    )
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        refresh_products_search_text(self.products.all())


class Brand(TimeStampedModel):
    """Бренд = виробник. Блок під каталогом на /products."""

    slug = models.SlugField('Slug', max_length=64, unique=True)
    name = models.CharField('Название', max_length=255)
    logo = models.ImageField(
        'Логотип',
        upload_to='catalog/brands/',
        blank=True,
        null=True,
    )
    short_description = models.TextField('Краткое описание', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)
    is_featured = models.BooleanField(
        'Под каталогом',
        default=True,
        help_text='Показывать в блоке производителей под каталогом на /products',
    )

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from .selectors import invalidate_catalog_list_cache

        invalidate_catalog_list_cache()
        refresh_products_search_text(self.products.all())

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
        verbose_name='Категория',
    )
    slug = models.SlugField('Slug', max_length=128, unique=True)
    name = models.CharField(
        'Название',
        max_length=255,
        help_text='Без дубля бренда, напр. Соус «Сладкий Чили»',
    )
    package = models.CharField(
        'Фасовка',
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
    extra_filters = models.ManyToManyField(
        'ProductFilter',
        verbose_name='Дополнительные фильтры',
        related_name='products',
        blank=True,
        help_text='Иконки свойств на карточке. Назначаются вручную.',
    )
    search_text = models.TextField(
        'Поисковый текст',
        blank=True,
        editable=False,
        help_text='Заполняется автоматически при сохранении товара.',
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['brand__order', 'order', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
        ]

    def __str__(self):
        return f'{self.brand.name} — {self.name} ({self.package})'

    def get_absolute_url(self) -> str:
        return reverse('product_detail', args=[self.slug])

    def is_snack(self) -> bool:
        category = self.category if self.category_id else None
        if category is None:
            return False
        if category.slug == 'snacks':
            return True
        parent = category.parent if category.parent_id else None
        return bool(parent and parent.slug == 'snacks')

    def build_search_text(self) -> str:
        """Назва/фасування/опис усіх мов + бренд + категорія, нормалізовані."""
        brand = self.brand if self.brand_id else None
        category = self.category if self.category_id else None
        parts = [
            *_translated_values(self, _SEARCH_TRANSLATED_FIELDS),
            *_translated_values(brand, ('name',)),
            *_translated_values(category, ('name',)),
        ]
        return build_search_text(parts)

    def save(self, *args, **kwargs):
        self.search_text = self.build_search_text()
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = {*update_fields, 'search_text'}
        super().save(*args, **kwargs)


class ProductFilter(TimeStampedModel):
    """Додатковий фільтр/властивість товару з іконкою (як на Krambals)."""

    slug = models.SlugField('Slug', max_length=64, unique=True)
    name = models.CharField('Название', max_length=128)
    icon = models.ImageField(
        'Иконка',
        upload_to='catalog/filters/',
        blank=True,
        null=True,
        help_text='Пусто — стандартная иконка из static/img/product-filters/.',
    )
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Фильтр товара'
        verbose_name_plural = 'Фильтры товаров'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


def refresh_products_search_text(queryset) -> int:
    """Перебудова search_text для набору товарів (після зміни бренду/категорії)."""
    products = list(queryset.select_related('brand', 'category'))
    changed = []
    for product in products:
        value = product.build_search_text()
        if value != product.search_text:
            product.search_text = value
            changed.append(product)
    if changed:
        Product.objects.bulk_update(changed, ['search_text'], batch_size=500)
    return len(changed)
