from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_legal_requisites_json'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaBlob',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'path',
                    models.CharField(
                        db_index=True,
                        max_length=500,
                        unique=True,
                        verbose_name='Путь',
                    ),
                ),
                ('data', models.BinaryField(verbose_name='Данные')),
                (
                    'content_type',
                    models.CharField(
                        default='application/octet-stream',
                        max_length=128,
                        verbose_name='Content-Type',
                    ),
                ),
                (
                    'size',
                    models.PositiveIntegerField(default=0, verbose_name='Размер'),
                ),
                (
                    'updated_at',
                    models.DateTimeField(auto_now=True, verbose_name='Обновлено'),
                ),
            ],
            options={
                'verbose_name': 'Медиафайл (БД)',
                'verbose_name_plural': 'Медиафайлы (БД)',
            },
        ),
    ]
