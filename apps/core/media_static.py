"""Map ephemeral /media logo URLs to shipped static files (Vercel)."""

from pathlib import Path

from django.http import Http404
from django.shortcuts import redirect
from django.templatetags.static import static

_SAFE_NAME = frozenset('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    if not name or any(ch not in _SAFE_NAME for ch in name):
        raise Http404()
    return name


def redirect_partner_logo(request, filename: str):
    name = _safe_filename(filename)
    return redirect(static(f'img/partners/{name}'))


def redirect_brand_logo(request, filename: str):
    name = _safe_filename(filename)
    return redirect(static(f'img/brands/{name}'))
