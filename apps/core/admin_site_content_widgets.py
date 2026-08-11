"""Dark-readable CMS widgets + Hex color picker for Unfold admin."""

from __future__ import annotations

from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget

try:
    from unfold.widgets import INPUT_CLASSES, TEXTAREA_CLASSES
except ImportError:  # pragma: no cover
    INPUT_CLASSES = ['border', 'rounded-default', 'px-3', 'py-2', 'w-full']
    TEXTAREA_CLASSES = INPUT_CLASSES

_SKIP_CLASSES = frozenset(
    {
        'bg-white',
        'text-font-default-light',
        'border-base-200',
        'dark:bg-base-900',
        'dark:border-base-700',
        'dark:text-font-default-dark',
    }
)
_FORCE_CLASSES = (
    'bg-base-900',
    'text-base-100',
    'border-base-700',
    'placeholder-base-400',
)


def cms_control_classes(base) -> list[str]:
    classes = [c for c in list(base) if c not in _SKIP_CLASSES]
    for item in _FORCE_CLASSES:
        if item not in classes:
            classes.append(item)
    return classes


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


class HexColorInputWidget(forms.TextInput):
    """Text hex field + native color picker (synced via small inline script)."""

    template_name = 'admin/widgets/hex_color.html'

    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        attrs.setdefault('maxlength', '7')
        attrs.setdefault('placeholder', '#FF5A36')
        attrs.setdefault('pattern', r'^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$')
        classes = cms_control_classes(INPUT_CLASSES)
        attrs['class'] = ' '.join([*classes, 'hex-color-input__text'])
        super().__init__(attrs=attrs)

    class Media:
        css = {'all': ('css/admin/hex_color.css',)}
        js = ('js/admin/hex_color.js',)


def apply_readable_widget(widget) -> None:
    """Mutate widget classes for dark Unfold readability."""
    from django.forms.widgets import CheckboxInput, ClearableFileInput, Select

    if isinstance(widget, (CheckboxInput, ClearableFileInput, Select, HexColorInputWidget)):
        return
    if isinstance(widget, forms.Textarea):
        widget.attrs['class'] = ' '.join(cms_control_classes(TEXTAREA_CLASSES))
    elif isinstance(widget, forms.TextInput):
        widget.attrs['class'] = ' '.join(cms_control_classes(INPUT_CLASSES))
