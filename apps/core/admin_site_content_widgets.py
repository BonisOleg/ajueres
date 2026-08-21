"""CMS widgets + hex color picker for Unfold (light-first, dark: variants)."""

from __future__ import annotations

from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget

try:
    from unfold.widgets import (
        INPUT_CLASSES,
        TEXTAREA_CLASSES,
        UnfoldAdminImageFieldWidget,
    )
except ImportError:  # pragma: no cover
    from django.contrib.admin.widgets import AdminFileWidget

    INPUT_CLASSES = ['border', 'rounded-default', 'px-3', 'py-2', 'w-full']
    TEXTAREA_CLASSES = INPUT_CLASSES
    UnfoldAdminImageFieldWidget = AdminFileWidget


def cms_control_classes(base) -> list[str]:
    return list(base)


class CmsAdminTextInputWidget(AdminTextInputWidget):
    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        existing = attrs.get('class', '')
        merged = cms_control_classes(INPUT_CLASSES)
        if existing:
            merged = list(dict.fromkeys([*merged, *str(existing).split()]))
        attrs['class'] = ' '.join(merged)
        super().__init__(attrs=attrs)


class CmsAdminTextareaWidget(AdminTextareaWidget):
    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        existing = attrs.get('class', '')
        merged = cms_control_classes(TEXTAREA_CLASSES)
        if existing:
            merged = list(dict.fromkeys([*merged, *str(existing).split()]))
        attrs['class'] = ' '.join(merged)
        super().__init__(attrs=attrs)


def file_preview_url(value) -> str:
    """Return media URL only when the file is actually available."""
    if not value:
        return ''
    name = getattr(value, 'name', None) or ''
    if not name:
        return ''
    storage = getattr(value, 'storage', None)
    if storage is not None:
        try:
            if not storage.exists(name):
                return ''
        except (OSError, ValueError):
            return ''
    try:
        return value.url or ''
    except (AttributeError, ValueError):
        return ''


class CmsAdminImageWidget(UnfoldAdminImageFieldWidget):
    """Image upload with a visible preview (uploaded file or static fallback)."""

    template_name = 'admin/widgets/cms_image.html'

    def __init__(self, attrs=None, preview_url=''):
        attrs = dict(attrs or {})
        attrs.setdefault('accept', 'image/jpeg,image/png,image/webp,image/gif')
        self.preview_url = preview_url or ''
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        url = file_preview_url(value) or self.preview_url
        ctx['widget']['preview_url'] = url
        return ctx


class HexColorInputWidget(forms.TextInput):
    """Hex field + circular picker; optional HSV wheel for any color."""

    template_name = 'admin/widgets/hex_color.html'

    def __init__(self, attrs=None, *, show_wheel=False):
        self.show_wheel = show_wheel
        attrs = dict(attrs or {})
        attrs.setdefault('maxlength', '7')
        attrs.setdefault('placeholder', '#FF5A36')
        attrs.setdefault('pattern', r'^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$')
        classes = cms_control_classes(INPUT_CLASSES)
        attrs['class'] = ' '.join([*classes, 'hex-color-input__text'])
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        ctx['widget']['show_wheel'] = self.show_wheel
        return ctx

    class Media:
        css = {'all': ('css/admin/hex_color.css',)}
        js = ('js/admin/hex_color.js',)


def apply_readable_widget(widget) -> None:
    """Keep text widgets on Unfold light-readable input classes."""
    from django.forms.widgets import CheckboxInput, ClearableFileInput, Select

    from .admin_requisites_widget import RequisitesRowsWidget

    if isinstance(
        widget,
        (CheckboxInput, ClearableFileInput, Select, HexColorInputWidget, RequisitesRowsWidget),
    ):
        return

    extra: list[str] = []
    if isinstance(widget, forms.Textarea):
        extra = cms_control_classes(TEXTAREA_CLASSES)
    elif isinstance(widget, forms.TextInput):
        extra = cms_control_classes(INPUT_CLASSES)
    if not extra:
        return
    existing = str(widget.attrs.get('class') or '').split()
    widget.attrs['class'] = ' '.join(dict.fromkeys([*extra, *existing]))
