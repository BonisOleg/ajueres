"""CMS section form + view (registry-driven SiteBlock editor)."""

from __future__ import annotations

from django import forms
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


def _field_name(page: str, key: str, suffix: str) -> str:
    return f'block__{page}__{key}__{suffix}'


def load_section_blocks(section) -> dict[tuple[str, str], SiteBlock]:
    result: dict[tuple[str, str], SiteBlock] = {}
    for page, key in section.blocks:
        defaults = {'text_html': BLOCK_DEFAULTS.get((page, key), '')}
        obj, _ = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults=defaults,
        )
        result[(page, key)] = obj
    return result


class SitePageContentForm(forms.Form):
    """Dynamically built from ContentSection.blocks."""

    def __init__(self, section, blocks_map, *args, **kwargs):
        self.section = section
        self.blocks_map = blocks_map
        super().__init__(*args, **kwargs)

        if section.visibility_key:
            vis_block = blocks_map.get((section.page_slug, section.visibility_key))
            initial = True
            if vis_block is not None:
                initial = (vis_block.text_html or '1').strip() in {
                    '1',
                    'true',
                    'yes',
                    'on',
                }
            self.fields['section_visible'] = forms.BooleanField(
                label=_('Показувати секцію на сайті'),
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
                initial = (block.text_html or '').strip() in {
                    '1',
                    'true',
                    'yes',
                    'on',
                }
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
                widget = (
                    CmsAdminTextInputWidget()
                    if key in INLINE_KEYS
                    else CmsAdminTextareaWidget(
                        attrs={'rows': 4 if key in MULTILINE_KEYS else 2}
                    )
                )
                self.fields[_field_name(page, key, 'text_html')] = forms.CharField(
                    label=label,
                    required=False,
                    initial=block.text_html or '',
                    widget=widget,
                )

    def save(self):
        section = self.section
        cleaned = self.cleaned_data

        if section.visibility_key:
            vis = '1' if cleaned.get('section_visible') else '0'
            block = self.blocks_map[(section.page_slug, section.visibility_key)]
            if block.text_html != vis:
                block.text_html = vis
                block.save(update_fields=['text_html'])

        for page, key in section.blocks:
            if section.visibility_key and key == section.visibility_key:
                continue
            block = self.blocks_map[(page, key)]
            btype = block_type(page, key)

            if btype == 'visibility' or is_visibility_key(key):
                val = '1' if cleaned.get(_field_name(page, key, 'visible')) else '0'
                if block.text_html != val:
                    block.text_html = val
                    block.save(update_fields=['text_html'])
            elif btype == 'image':
                image = cleaned.get(_field_name(page, key, 'image'))
                if image:
                    block.image = image
                    block.save(update_fields=['image'])
            else:
                text = cleaned.get(_field_name(page, key, 'text_html'), '')
                if block.text_html != text:
                    block.text_html = text
                    block.save(update_fields=['text_html'])

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
            messages.success(request, _('Контент секції збережено.'))
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
        fields = []
        for key in group.keys:
            for suffix in ('text_html', 'image', 'visible'):
                name = _field_name(section.page_slug, key, suffix)
                if name in form.fields:
                    fields.append(form[name])
                    used_names.add(name)
        if fields:
            grouped_fields.append({'title': group.title, 'fields': fields})

    leftover = [form[name] for name in form.fields if name not in used_names]
    if leftover:
        grouped_fields.append({'title': _('Інше'), 'fields': leftover})

    context = {
        **model_admin.admin_site.each_context(request),
        'title': section.title,
        'section': section,
        'form': form,
        'grouped_fields': grouped_fields,
        'opts': model_admin.model._meta,
        'has_view_permission': True,
        'has_change_permission': True,
        'style_url': style_url,
        'media': form.media,
    }
    return render(request, 'admin/core/site_content_page.html', context)
