"""Shared Unfold admin mixins."""

from __future__ import annotations

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from .admin_site_content_widgets import apply_readable_widget


class SingletonModelAdminMixin:
    """changelist → change pk=1; no delete; add only if missing."""

    singleton_pk = 1

    def has_add_permission(self, request):
        model = self.model
        return not model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = self.model.objects.get_or_create(pk=self.singleton_pk)
        return HttpResponseRedirect(
            reverse(
                f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
                args=[obj.pk],
            )
        )


class ReadableUnfoldFieldsMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and formfield.widget is not None:
            apply_readable_widget(formfield.widget)
        return formfield


class ImagePreviewMixin:
    preview_field = 'image'
    preview_max_height = 80

    def get_image_preview(self, obj):
        field = getattr(obj, self.preview_field, None)
        if not field:
            return '—'
        try:
            url = field.url
        except ValueError:
            return '—'
        return format_html(
            '<img src="{}" alt="" style="max-height:{}px;width:auto;border-radius:6px;">',
            url,
            self.preview_max_height,
        )

    get_image_preview.short_description = 'Превʼю'
