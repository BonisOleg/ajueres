"""Unfold admin branding: light palette, logo, favicons, assets."""

from __future__ import annotations

from django.http import HttpRequest
from django.templatetags.static import static

# Site tokens: orange #ff5a36, navy #0f1835, green #1fa968, blue #3e7bfa.
UNFOLD_COLORS = {
    'base': {
        '50': '#fbf7f2',
        '100': '#f3eee6',
        '200': '#ede7de',
        '300': '#d0c6b8',
        '400': '#a89c8e',
        '500': '#6e655b',
        '600': '#3d4757',
        '700': '#243044',
        '800': '#152036',
        '900': '#0f1835',
        '950': '#0a1024',
    },
    'primary': {
        '50': '#fff4ef',
        '100': '#ffe6da',
        '200': '#ffcdb8',
        '300': '#ffa888',
        '400': '#ff7a52',
        '500': '#ff5a36',
        '600': '#db3f1c',
        '700': '#b83318',
        '800': '#8f2712',
        '900': '#6b1d0e',
        '950': '#3d1008',
    },
    'font': {
        'subtle-light': 'var(--color-base-500)',
        'subtle-dark': 'var(--color-base-400)',
        'default-light': 'var(--color-base-700)',
        'default-dark': 'var(--color-base-300)',
        'important-light': 'var(--color-base-900)',
        'important-dark': 'var(--color-base-100)',
    },
    'green': {
        '50': '#eaf8f0',
        '100': '#d8f2e5',
        '200': '#b3e4cb',
        '300': '#7dd0a8',
        '400': '#3db87e',
        '500': '#1fa968',
        '600': '#188a54',
        '700': '#146e43',
        '800': '#105536',
        '900': '#0c3f28',
        '950': '#072418',
    },
    'blue': {
        '50': '#e2eaff',
        '100': '#c9d7ff',
        '200': '#a3baff',
        '300': '#7a9bff',
        '400': '#5684fc',
        '500': '#3e7bfa',
        '600': '#2f6fed',
        '700': '#2458c4',
        '800': '#1a3f8f',
        '900': '#122a5c',
        '950': '#0a1838',
    },
}

_LOGO_MARK = 'img/icons/favicon.png'


def unfold_colors(request: HttpRequest | None = None) -> dict[str, dict[str, str]]:
    return {name: dict(weights) for name, weights in UNFOLD_COLORS.items()}


def site_logo(request: HttpRequest | None = None) -> str:
    return static(_LOGO_MARK)


def site_favicons(request: HttpRequest | None = None) -> list[dict[str, str]]:
    return [
        {
            'href': static('favicon.ico'),
            'rel': 'icon',
            'sizes': 'any',
        },
        {
            'href': static('img/icons/favicon-16x16.png'),
            'rel': 'icon',
            'type': 'image/png',
            'sizes': '16x16',
        },
        {
            'href': static('img/icons/favicon-32x32.png'),
            'rel': 'icon',
            'type': 'image/png',
            'sizes': '32x32',
        },
        {
            'href': static('img/icons/favicon-192x192.png'),
            'rel': 'icon',
            'type': 'image/png',
            'sizes': '192x192',
        },
        {
            'href': static(_LOGO_MARK),
            'rel': 'icon',
            'type': 'image/png',
            'sizes': '512x512',
        },
        {
            'href': static('img/icons/apple-touch-icon.png'),
            'rel': 'apple-touch-icon',
            'type': 'image/png',
            'sizes': '180x180',
        },
    ]


def admin_styles(request: HttpRequest | None = None) -> str:
    return static('css/admin/unfold_theme.css')


def admin_scripts(request: HttpRequest | None = None) -> str:
    return static('js/admin/unfold_default_light.js')
