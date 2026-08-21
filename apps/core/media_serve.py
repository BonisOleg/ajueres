"""Serve /media/ from disk, with MediaBlob fallback on Vercel."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.static import serve as static_serve


def serve_media(request, path: str):
    """Filesystem first; durable DB blob when /tmp media is gone."""
    media_root = Path(settings.MEDIA_ROOT)
    full = media_root / path
    if full.is_file():
        return static_serve(request, path, document_root=str(media_root))

    if not getattr(settings, 'IS_VERCEL', False):
        raise Http404('Media not found')

    from .media_models import MediaBlob

    blob = MediaBlob.objects.filter(path=path).only('data', 'content_type').first()
    if blob is None:
        raise Http404('Media not found')

    # Warm /tmp so subsequent ImageField.open / exists work on this instance.
    try:
        full.parent.mkdir(parents=True, exist_ok=True)
        if not full.is_file():
            full.write_bytes(bytes(blob.data))
    except OSError:
        pass

    return HttpResponse(bytes(blob.data), content_type=blob.content_type)
