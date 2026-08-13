from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_siteblock_text_html_translation'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteFooterSettings',
            fields=[],
            options={
                'verbose_name': 'Подвал сайта',
                'verbose_name_plural': 'Подвал сайта',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.sitesettings',),
        ),
        migrations.CreateModel(
            name='SiteHeaderSettings',
            fields=[],
            options={
                'verbose_name': 'Шапка сайта',
                'verbose_name_plural': 'Шапка сайта',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.sitesettings',),
        ),
        migrations.AlterModelOptions(
            name='aboutaboutsettings',
            options={
                'verbose_name': 'О компании — Шапка',
                'verbose_name_plural': 'О компании — Шапка',
            },
        ),
        migrations.AlterModelOptions(
            name='contactscontactssettings',
            options={
                'verbose_name': 'Контакты — Тексты',
                'verbose_name_plural': 'Контакты — Тексты',
            },
        ),
        migrations.AddField(
            model_name='blockstyle',
            name='bg_image',
            field=models.ImageField(
                blank=True,
                help_text='Если задано — покрывает секцию. Цвет остаётся запасным фоном.',
                null=True,
                upload_to='cms/section-bg/',
                verbose_name='Фоновое изображение',
            ),
        ),
    ]
