from django.core.files.storage import FileSystemStorage

from .image_webp import maybe_webp_upload


class WebPFileSystemStorage(FileSystemStorage):
    """Media storage that stores raster uploads as WebP."""

    def save(self, name, content, max_length=None):
        name, content = maybe_webp_upload(name, content)
        return super().save(name, content, max_length=max_length)
