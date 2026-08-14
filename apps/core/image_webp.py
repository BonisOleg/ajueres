"""Convert uploaded raster images to WebP before they hit media storage."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError

WEBP_QUALITY = 82
_SKIP_SUFFIXES = frozenset({'.webp', '.svg', '.pdf', '.eps', '.ai'})


def _read_bytes(content) -> bytes:
    if hasattr(content, 'chunks'):
        return b''.join(content.chunks())
    position = 0
    if hasattr(content, 'tell'):
        try:
            position = content.tell()
        except OSError:
            position = 0
    if hasattr(content, 'seek'):
        try:
            content.seek(0)
        except OSError:
            pass
    data = content.read()
    if hasattr(content, 'seek'):
        try:
            content.seek(position)
        except OSError:
            pass
    return data if isinstance(data, (bytes, bytearray)) else b''


def _has_alpha(image: Image.Image) -> bool:
    if image.mode in {'RGBA', 'LA', 'PA'}:
        return True
    if image.mode == 'P' and 'transparency' in image.info:
        return True
    return False


def raster_to_webp_bytes(data: bytes) -> bytes | None:
    if not data:
        return None
    try:
        image = Image.open(BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        return None

    if image.format == 'WEBP':
        return None

    if _has_alpha(image):
        converted = image.convert('RGBA')
    else:
        converted = image.convert('RGB')

    buffer = BytesIO()
    converted.save(
        buffer,
        format='WEBP',
        quality=WEBP_QUALITY,
        method=4,
    )
    return buffer.getvalue()


def maybe_webp_upload(name: str, content):
    """Return (name, content) as WebP, or the originals if conversion is skipped."""
    suffix = Path(name or '').suffix.lower()
    if suffix in _SKIP_SUFFIXES:
        return name, content

    payload = _read_bytes(content)
    webp = raster_to_webp_bytes(payload)
    if not webp:
        original_name = Path(name or 'file').name
        return name, ContentFile(payload, name=original_name)

    stem = Path(name).stem if name else 'image'
    parent = str(Path(name).parent) if name else ''
    new_name = f'{stem}.webp'
    if parent and parent != '.':
        new_name = f'{parent}/{new_name}'
    return new_name, ContentFile(webp, name=Path(new_name).name)


def convert_stored_image(storage, name: str, *, write: bool = True) -> str | None:
    """Return target WebP storage name for an existing file. Optionally write it."""
    if not name:
        return None
    suffix = Path(name).suffix.lower()
    if suffix in _SKIP_SUFFIXES:
        return None
    if not storage.exists(name):
        return None
    with storage.open(name, 'rb') as handle:
        payload = handle.read()
    webp = raster_to_webp_bytes(payload)
    if not webp:
        return None
    new_name = str(Path(name).with_suffix('.webp'))
    if not write:
        return new_name
    return storage.save(new_name, ContentFile(webp, name=Path(new_name).name))
