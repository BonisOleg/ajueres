"""Shared Unfold admin mixins."""

from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.db.models.deletion import ProtectedError, RestrictedError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from .admin_site_content_widgets import apply_readable_widget

_SAVE_ERRORS = (ValidationError, IntegrityError, ProtectedError, RestrictedError)


def format_admin_save_error(exc: BaseException) -> str:
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
    return str(exc) or 'Ошибка сохранения.'


class ImageAcceptMixin:
    """Unfold image preview requires accept=image/* on the file widget."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and isinstance(db_field, models.ImageField):
            formfield.widget.attrs.setdefault('accept', 'image/*')
        return formfield


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


class UnfoldTranslationAdmin(
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

    get_image_preview.short_description = 'Превью'
