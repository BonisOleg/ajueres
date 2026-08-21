from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from .image_webp import maybe_webp_upload


def _guess_content_type(name: str) -> str:
    lower = (name or '').lower()
    if lower.endswith('.webp'):
        return 'image/webp'
    if lower.endswith('.png'):
        return 'image/png'
    if lower.endswith(('.jpg', '.jpeg')):
        return 'image/jpeg'
    if lower.endswith('.gif'):
        return 'image/gif'
    return 'application/octet-stream'


def _read_content_bytes(content) -> bytes:
    if hasattr(content, 'open'):
        try:
            content.open('rb')
        except Exception:
            pass
    if hasattr(content, 'seek'):
        try:
            content.seek(0)
        except Exception:
            pass
    raw = content.read() if hasattr(content, 'read') else bytes(content)
    if hasattr(content, 'seek'):
        try:
            content.seek(0)
        except Exception:
            pass
    return raw


def _persist_media_blob(name: str, content) -> None:
    """Store a durable copy when the local media root is ephemeral."""
    if not getattr(settings, 'IS_VERCEL', False):
        return
    from .media_models import MediaBlob

    raw = _read_content_bytes(content)
    MediaBlob.objects.update_or_create(
        path=name,
        defaults={
            'data': raw,
            'content_type': _guess_content_type(name),
            'size': len(raw),
        },
    )


def _hydrate_media_blob(storage: FileSystemStorage, name: str) -> bool:
    """Materialize a DB blob into MEDIA_ROOT for FileSystemStorage APIs."""
    if not getattr(settings, 'IS_VERCEL', False):
        return False
    path = Path(storage.path(name))
    if path.is_file():
        return True
    from .media_models import MediaBlob

    blob = MediaBlob.objects.filter(path=name).only('data').first()
    if blob is None:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(blob.data))
    return True


class WebPFileSystemStorage(FileSystemStorage):
    """Media storage that stores raster uploads as WebP (+ DB on Vercel)."""

    def save(self, name, content, max_length=None):
        name, content = maybe_webp_upload(name, content)
        saved = super().save(name, content, max_length=max_length)
        try:
            with self.open(saved, 'rb') as stored:
                _persist_media_blob(saved, stored)
        except Exception:
            _persist_media_blob(saved, content)
        return saved

    def exists(self, name):
        if super().exists(name):
            return True
        if not getattr(settings, 'IS_VERCEL', False):
            return False
        from .media_models import MediaBlob

        return MediaBlob.objects.filter(path=name).exists()

    def open(self, name, mode='rb'):
        if 'r' in mode:
            _hydrate_media_blob(self, name)
        return super().open(name, mode)

    def delete(self, name):
        super().delete(name)
        if getattr(settings, 'IS_VERCEL', False):
            from .media_models import MediaBlob

            MediaBlob.objects.filter(path=name).delete()

    def size(self, name):
        _hydrate_media_blob(self, name)
        return super().size(name)
