"""Unfold widget: one admin row per requisite (label, value, delete)."""

from __future__ import annotations

import json

from django import forms

from .requisites import normalize_requisites


class RequisitesRowsWidget(forms.Widget):
    template_name = 'admin/widgets/requisites_rows.html'

    def format_value(self, value):
        return json.dumps(normalize_requisites(value), ensure_ascii=False)

    def value_from_datadict(self, data, files, name):
        raw = data.get(name)
        return normalize_requisites(raw)

    def get_context(self, name, value, attrs):
        ctx = super().get_context(name, value, attrs)
        rows = normalize_requisites(value)
        ctx['widget']['rows'] = rows
        ctx['widget']['json_value'] = self.format_value(value)
        return ctx

    class Media:
        css = {'all': ('css/admin/requisites_rows.css',)}
        js = ('js/admin/requisites_rows.js',)
