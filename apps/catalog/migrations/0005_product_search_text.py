from django.db import migrations, models

from apps.catalog.search import build_search_text


def _languages():
    from django.conf import settings

    codes = getattr(settings, 'MODELTRANSLATION_LANGUAGES', None)
    if not codes:
        codes = [code for code, _ in getattr(settings, 'LANGUAGES', [])]
    return [code.replace('-', '_') for code in codes]


def _build(product, langs) -> str:
    parts = []
    for base in ('name', 'package', 'description'):
        for lang in langs:
            parts.append(getattr(product, f'{base}_{lang}', '') or '')
    parts.append(product.brand.name if product.brand_id else '')
    if product.category_id:
        for lang in langs:
            parts.append(getattr(product.category, f'name_{lang}', '') or '')
    return build_search_text(parts)


def backfill(apps, schema_editor):
    Product = apps.get_model('catalog', 'Product')
    langs = _languages()
    batch = []
    qs = Product.objects.select_related('brand', 'category').iterator(chunk_size=500)
    for product in qs:
        product.search_text = _build(product, langs)
        batch.append(product)
        if len(batch) >= 500:
            Product.objects.bulk_update(batch, ['search_text'])
            batch = []
    if batch:
        Product.objects.bulk_update(batch, ['search_text'])


class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0004_category_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='search_text',
            field=models.TextField(
                blank=True,
                editable=False,
                help_text='Заповнюється автоматично при збереженні товару.',
                verbose_name='Пошуковий текст',
            ),
        ),
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
