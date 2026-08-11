"""CMS section form + view (registry-driven SiteBlock editor)."""

from __future__ import annotations

from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .admin_site_content_widgets import CmsAdminTextareaWidget, CmsAdminTextInputWidget
from .block_defaults import (
    BLOCK_DEFAULTS,
    BLOCK_LABELS,
    INLINE_KEYS,
    MULTILINE_KEYS,
    block_type,
    is_visibility_key,
)
from .models import BlockStyle, SiteBlock, SiteSettings
from .selectors import invalidate_site_blocks_cache
from .site_content_registry import get_section

try:
    from unfold.widgets import UnfoldAdminFileFieldWidget, UnfoldBooleanWidget
except ImportError:  # pragma: no cover
    UnfoldAdminFileFieldWidget = forms.ClearableFileInput
    UnfoldBooleanWidget = forms.CheckboxInput

CMS_LANGS = tuple(getattr(settings, 'MODELTRANSLATION_LANGUAGES', ('ru', 'uz', 'en')))
CMS_LANG_LABELS = {
    'ru': 'RU',
    'uz': 'UZ',
    'en': 'EN',
}


def _field_name(page: str, key: str, suffix: str) -> str:
    return f'block__{page}__{key}__{suffix}'


def _truthy(raw: str) -> bool:
    return (raw or '').strip().lower() in {'1', 'true', 'yes', 'on'}


def load_section_blocks(section) -> dict[tuple[str, str], SiteBlock]:
    result: dict[tuple[str, str], SiteBlock] = {}
    for page, key in section.blocks:
        default_text = BLOCK_DEFAULTS.get((page, key), '')
        defaults = {'text_html': default_text}
        # Prefill default language column when modeltranslation is active.
        defaults['text_html_ru'] = default_text
        obj, created = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults=defaults,
        )
        if created is False and default_text and not (obj.text_html_ru or obj.text_html):
            obj.text_html_ru = default_text
            obj.text_html = default_text
            obj.save(update_fields=['text_html', 'text_html_ru'])
        result[(page, key)] = obj
    return result


class SitePageContentForm(forms.Form):
    """Dynamically built from ContentSection.blocks (text fields × languages)."""

    def __init__(self, section, blocks_map, *args, **kwargs):
        self.section = section
        self.blocks_map = blocks_map
        super().__init__(*args, **kwargs)

        if section.visibility_key:
            vis_block = blocks_map.get((section.page_slug, section.visibility_key))
            initial = True
            if vis_block is not None:
                initial = _truthy(vis_block.text_html_ru or vis_block.text_html or '1')
            self.fields['section_visible'] = forms.BooleanField(
                label=_('Показывать секцию на сайте'),
                required=False,
                initial=initial,
                widget=UnfoldBooleanWidget(),
            )

        for page, key in section.blocks:
            if section.visibility_key and key == section.visibility_key:
                continue
            block = blocks_map[(page, key)]
            label = BLOCK_LABELS.get((page, key), key)
            btype = block_type(page, key)

            if btype == 'visibility' or is_visibility_key(key):
                initial = _truthy(block.text_html_ru or block.text_html)
                self.fields[_field_name(page, key, 'visible')] = forms.BooleanField(
                    label=label,
                    required=False,
                    initial=initial,
                    widget=UnfoldBooleanWidget(),
                )
            elif btype == 'image':
                self.fields[_field_name(page, key, 'image')] = forms.ImageField(
                    label=label,
                    required=False,
                    widget=UnfoldAdminFileFieldWidget(),
                )
            else:
                for lang in CMS_LANGS:
                    widget = (
                        CmsAdminTextInputWidget()
                        if key in INLINE_KEYS
                        else CmsAdminTextareaWidget(
                            attrs={'rows': 4 if key in MULTILINE_KEYS else 2}
                        )
                    )
                    attr = f'text_html_{lang}'
                    initial = getattr(block, attr, None)
                    if initial is None:
                        initial = block.text_html if lang == 'ru' else ''
                    self.fields[_field_name(page, key, attr)] = forms.CharField(
                        label=f'{label} [{CMS_LANG_LABELS.get(lang, lang.upper())}]',
                        required=False,
                        initial=initial or '',
                        widget=widget,
                    )

    def save(self):
        section = self.section
        cleaned = self.cleaned_data

        if section.visibility_key:
            vis = '1' if cleaned.get('section_visible') else '0'
            block = self.blocks_map[(section.page_slug, section.visibility_key)]
            block.text_html = vis
            block.text_html_ru = vis
            for lang in CMS_LANGS:
                if lang != 'ru':
                    setattr(block, f'text_html_{lang}', vis)
            block.save()

        for page, key in section.blocks:
            if section.visibility_key and key == section.visibility_key:
                continue
            block = self.blocks_map[(page, key)]
            btype = block_type(page, key)

            if btype == 'visibility' or is_visibility_key(key):
                val = '1' if cleaned.get(_field_name(page, key, 'visible')) else '0'
                block.text_html = val
                block.text_html_ru = val
                for lang in CMS_LANGS:
                    if lang != 'ru':
                        setattr(block, f'text_html_{lang}', val)
                block.save()
            elif btype == 'image':
                image = cleaned.get(_field_name(page, key, 'image'))
                if image:
                    block.image = image
                    block.save(update_fields=['image'])
            else:
                for lang in CMS_LANGS:
                    attr = f'text_html_{lang}'
                    text = cleaned.get(_field_name(page, key, attr), '')
                    setattr(block, attr, text)
                # Keep canonical text_html in sync with default language.
                block.text_html = getattr(block, 'text_html_ru', '') or ''
                block.save()

        invalidate_site_blocks_cache(section.page_slug)


def site_content_section_view(request, page_slug: str, section_slug: str, model_admin):
    section = get_section(page_slug, section_slug)
    if section is None:
        raise Http404('Unknown content section')

    SiteSettings.objects.get_or_create(pk=1)
    blocks_map = load_section_blocks(section)

    style_obj = None
    if section.style_section_key:
        BlockStyle.ensure_defaults()
        style_obj, _ = BlockStyle.objects.get_or_create(
            page=section.page_slug,
            section_key=section.style_section_key,
            defaults={'label': section.title},
        )

    if request.method == 'POST':
        form = SitePageContentForm(section, blocks_map, request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('Контент секции сохранён.'))
            return HttpResponseRedirect(request.path)
    else:
        form = SitePageContentForm(section, blocks_map)

    style_url = ''
    if style_obj is not None:
        style_url = reverse('admin:core_blockstyle_change', args=[style_obj.pk])

    grouped_fields = []
    used_names: set[str] = set()
    if form.fields.get('section_visible'):
        used_names.add('section_visible')

    for group in section.field_groups:
        shared_fields = []
        lang_fields: dict[str, list] = {lang: [] for lang in CMS_LANGS}
        for key in group.keys:
            image_name = _field_name(section.page_slug, key, 'image')
            visible_name = _field_name(section.page_slug, key, 'visible')
            if image_name in form.fields:
                shared_fields.append(form[image_name])
                used_names.add(image_name)
            elif visible_name in form.fields:
                shared_fields.append(form[visible_name])
                used_names.add(visible_name)
            else:
                for lang in CMS_LANGS:
                    name = _field_name(section.page_slug, key, f'text_html_{lang}')
                    if name in form.fields:
                        lang_fields[lang].append(form[name])
                        used_names.add(name)
        grouped_fields.append(
            {
                'title': group.title,
                'shared_fields': shared_fields,
                'lang_panels': [
                    {
                        'code': lang,
                        'label': CMS_LANG_LABELS.get(lang, lang.upper()),
                        'fields': lang_fields[lang],
                    }
                    for lang in CMS_LANGS
                ],
                'has_langs': any(lang_fields.values()),
            }
        )

    leftover = [form[name] for name in form.fields if name not in used_names]
    if leftover:
        grouped_fields.append(
            {
                'title': _('Прочее'),
                'shared_fields': leftover,
                'lang_panels': [],
                'has_langs': False,
            }
        )

    context = {
        **model_admin.admin_site.each_context(request),
        'title': section.title,
        'section': section,
        'form': form,
        'grouped_fields': grouped_fields,
        'cms_langs': [
            {'code': lang, 'label': CMS_LANG_LABELS.get(lang, lang.upper())}
            for lang in CMS_LANGS
        ],
        'opts': model_admin.model._meta,
        'has_view_permission': True,
        'has_change_permission': True,
        'style_url': style_url,
        'media': form.media,
    }
    return render(request, 'admin/core/site_content_page.html', context)
