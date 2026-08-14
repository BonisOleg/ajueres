from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_blockstyle_bg_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='legaldocument',
            name='requisites',
            field=models.TextField(
                blank=True,
                help_text='Блок внизу публичной оферты. Можно заполнить позже.',
                verbose_name='Реквизиты',
            ),
        ),
        migrations.AddField(
            model_name='legaldocument',
            name='requisites_en',
            field=models.TextField(
                blank=True,
                help_text='Блок внизу публичной оферты. Можно заполнить позже.',
                null=True,
                verbose_name='Реквизиты',
            ),
        ),
        migrations.AddField(
            model_name='legaldocument',
            name='requisites_ru',
            field=models.TextField(
                blank=True,
                help_text='Блок внизу публичной оферты. Можно заполнить позже.',
                null=True,
                verbose_name='Реквизиты',
            ),
        ),
        migrations.AddField(
            model_name='legaldocument',
            name='requisites_uz',
            field=models.TextField(
                blank=True,
                help_text='Блок внизу публичной оферты. Можно заполнить позже.',
                null=True,
                verbose_name='Реквизиты',
            ),
        ),
    ]
