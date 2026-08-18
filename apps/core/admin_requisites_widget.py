"""Unfold widget: INN / account / bank / address plus optional extra rows."""

from __future__ import annotations

import json

from django import forms

from .requisites import display_requisites_rows, lang_from_field_name, normalize_requisites


class RequisitesRowsWidget(forms.Widget):
    template_name = 'admin/widgets/requisites_rows.html'

    def format_value(self, value):
        return json.dumps(normalize_requisites(value), ensure_ascii=False)

    def value_from_datadict(self, data, files, name):
        raw = data.get(name)
        return normalize_requisites(raw)

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        lang = lang_from_field_name(name)
        rows = display_requisites_rows(value, lang)
        ctx['widget']['standard_rows'] = rows[:4]
        ctx['widget']['extra_rows'] = rows[4:]
        ctx['widget']['json_value'] = json.dumps(rows, ensure_ascii=False)
        return ctx

    class Media:
        css = {'all': ('css/admin/requisites_rows.css',)}
        js = ('js/admin/requisites_rows.js',)
