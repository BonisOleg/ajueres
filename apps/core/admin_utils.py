"""Shared Unfold admin mixins."""

from __future__ import annotations

from django import forms
from django.contrib import messages
from django.core.exceptions import SuspiciousFileOperation, ValidationError
from django.db import IntegrityError, models
from django.db.models.deletion import ProtectedError, RestrictedError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from .admin_guidelines import (
    apply_image_guidelines,
    apply_text_guidelines,
    friendly_upload_exception,
)
from .admin_site_content_widgets import CmsAdminImageWidget, apply_readable_widget

_SAVE_ERRORS = (
    ValidationError,
    IntegrityError,
    ProtectedError,
    RestrictedError,
    SuspiciousFileOperation,
    OSError,
    ValueError,
)


def format_admin_save_error(exc: BaseException) -> str:
    mapped = friendly_upload_exception(exc)
    if mapped:
        return mapped
    if isinstance(exc, ValidationError):
        if getattr(exc, 'message_dict', None):
            parts = []
            for field, msgs in exc.message_dict.items():
                text = '; '.join(str(msg) for msg in msgs)
                if field == '__all__':
                    parts.append(text)
                else:
                    parts.append(f'{field}: {text}')
            return ' '.join(parts) or 'Ошибка сохранения.'
        msgs = getattr(exc, 'messages', None)
        if msgs:
            return '; '.join(str(msg) for msg in msgs)
    return str(exc) or 'Ошибка сохранения. Проверьте поля и загруженные файлы.'


class ImageAcceptMixin:
    """Every ImageField uses a preview widget (uploaded file or fallback URL)."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.ImageField):
            kwargs.setdefault('widget', CmsAdminImageWidget())
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and isinstance(db_field, models.ImageField):
            if not isinstance(formfield.widget, CmsAdminImageWidget):
                formfield.widget = CmsAdminImageWidget(
                    attrs=getattr(formfield.widget, 'attrs', None),
                )
            formfield.widget.attrs.setdefault('accept', 'image/jpeg,image/png,image/webp,image/gif')
            apply_image_guidelines(formfield, field_name=db_field.name)
        elif formfield is not None and isinstance(
            formfield, (forms.CharField, forms.EmailField)
        ):
            apply_text_guidelines(formfield, field_name=db_field.name)
        return formfield

    def get_image_fallback_urls(self, obj) -> dict:
        return {}

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            return form
        for name, url in self.get_image_fallback_urls(obj).items():
            field = form.base_fields.get(name)
            if field is None or not url:
                continue
            widget = field.widget
            if isinstance(widget, CmsAdminImageWidget):
                widget.preview_url = url
        return form


class SaveErrorMessageMixin:
    """Show the real save error instead of a blank 500 page."""

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            return super().changeform_view(
                request, object_id, form_url, extra_context
            )
        except _SAVE_ERRORS as exc:
            self.message_user(request, format_admin_save_error(exc), messages.ERROR)
            if request.method == 'POST':
                return HttpResponseRedirect(request.get_full_path())
            raise


class HideOrderAdminMixin:
    """Keep model.order for site sorting; hide it in Unfold admin."""

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        editable = getattr(self, 'list_editable', ()) or ()
        self.list_editable = tuple(name for name in editable if name != 'order')

    def get_list_display(self, request):
        return tuple(
            name for name in super().get_list_display(request) if name != 'order'
        )

    def get_exclude(self, request, obj=None):
        excluded = list(super().get_exclude(request, obj) or ())
        if 'order' not in excluded:
            names = {field.name for field in self.model._meta.fields}
            if 'order' in names:
                excluded.append('order')
        return excluded or None


class UnfoldTranslationAdmin(
    HideOrderAdminMixin,
    SaveErrorMessageMixin,
    ImageAcceptMixin,
    ModelAdmin,
    TabbedTranslationAdmin,
):
    """Unfold ModelAdmin + modeltranslation language tabs (MRO: Unfold first)."""


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


class ReadableUnfoldFieldsMixin(SaveErrorMessageMixin, ImageAcceptMixin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and formfield.widget is not None:
            apply_readable_widget(formfield.widget)
        return formfield


class ImagePreviewMixin:
    preview_field = 'image'
    preview_max_height = 80

    def get_preview_fallback_url(self, obj) -> str:
        urls = self.get_image_fallback_urls(obj) if hasattr(self, 'get_image_fallback_urls') else {}
        return urls.get(self.preview_field, '') or ''

    def get_image_preview(self, obj):
        from .admin_site_content_widgets import file_preview_url

        field = getattr(obj, self.preview_field, None)
        url = file_preview_url(field) or self.get_preview_fallback_url(obj)
        if not url:
            return '—'
        return format_html(
            '<img src="{}" alt="" class="admin-image-preview__thumb" '
            'style="max-height:{}px;width:auto;border-radius:6px;">',
            url,
            self.preview_max_height,
        )

    get_image_preview.short_description = 'Превью'
