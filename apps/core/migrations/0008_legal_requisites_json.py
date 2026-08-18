import json

from django.db import migrations, models


def convert_requisites_text_to_json(apps, schema_editor):
    LegalDocument = apps.get_model('core', 'LegalDocument')
    fields = ('requisites', 'requisites_ru', 'requisites_uz', 'requisites_en')

    def parse_text(text: str) -> list:
        rows = []
        for line in str(text).splitlines():
            raw = line.strip()
            if not raw:
                continue
            if ':' in raw:
                label, value = raw.split(':', 1)
                rows.append({'label': label.strip(), 'value': value.strip()})
            else:
                rows.append({'label': '', 'value': raw})
        return rows

    def as_rows(raw) -> list | None:
        if raw is None:
            return None
        if isinstance(raw, list):
            items = raw
        else:
            text = str(raw).strip()
            if not text:
                return []
            if text.startswith('['):
                try:
                    loaded = json.loads(text)
                except json.JSONDecodeError:
                    return parse_text(text)
                items = loaded if isinstance(loaded, list) else parse_text(text)
            else:
                return parse_text(text)
        rows = []
        for item in items:
            if not isinstance(item, dict):
                continue
            label = str(item.get('label') or '').strip()
            value = str(item.get('value') or '').strip()
            if label or value:
                rows.append({'label': label, 'value': value})
        return rows

    for obj in LegalDocument.objects.all():
        updates = {}
        for field in fields:
            rows = as_rows(getattr(obj, field))
            if rows is None:
                continue
            updates[field] = json.dumps(rows, ensure_ascii=False)
        if updates:
            LegalDocument.objects.filter(pk=obj.pk).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_seed_legal_documents'),
    ]

    operations = [
        migrations.RunPython(convert_requisites_text_to_json, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='legaldocument',
            name='requisites',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Отдельные строки: подпись и значение. Пустую строку можно удалить.',
                verbose_name='Реквизиты',
            ),
        ),
        migrations.AlterField(
            model_name='legaldocument',
            name='requisites_en',
            field=models.JSONField(
                blank=True,
                help_text='Отдельные строки: подпись и значение. Пустую строку можно удалить.',
                null=True,
                verbose_name='Реквизиты',
            ),
        ),
        migrations.AlterField(
            model_name='legaldocument',
            name='requisites_ru',
            field=models.JSONField(
                blank=True,
                help_text='Отдельные строки: подпись и значение. Пустую строку можно удалить.',
                null=True,
                verbose_name='Реквизиты',
            ),
        ),
        migrations.AlterField(
            model_name='legaldocument',
            name='requisites_uz',
            field=models.JSONField(
                blank=True,
                help_text='Отдельные строки: подпись и значение. Пустую строку можно удалить.',
                null=True,
                verbose_name='Реквизиты',
            ),
        ),
    ]
