"""Proxy SiteSettings subclasses — CMS sidebar slots (no admin imports)."""

from __future__ import annotations

from .models import SiteSettings
from .site_content_registry import CONTENT_SECTIONS


def _make_proxy(section):
    class_name = ''.join(
        part.capitalize()
        for part in f'{section.page_slug}_{section.slug}_settings'.split('_')
    )
    meta = type(
        'Meta',
        (),
        {
            'proxy': True,
            'app_label': 'core',
            'verbose_name': section.title,
            'verbose_name_plural': section.title,
        },
    )
    return type(
        class_name,
        (SiteSettings,),
        {
            '__module__': __name__,
            'Meta': meta,
        },
    )


SECTION_PROXY_MODELS: list[tuple[type, str, str]] = []

for _section in CONTENT_SECTIONS:
    _proxy = _make_proxy(_section)
    globals()[_proxy.__name__] = _proxy
    SECTION_PROXY_MODELS.append((_proxy, _section.page_slug, _section.slug))
