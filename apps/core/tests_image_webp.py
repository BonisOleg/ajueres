from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from PIL import Image

from apps.core.image_webp import (
    convert_stored_image,
    maybe_webp_upload,
    raster_to_webp_bytes,
)
from apps.core.webp_storage import WebPFileSystemStorage


def _png_bytes(size=(12, 8), color=(20, 80, 180), mode='RGB') -> bytes:
    image = Image.new(mode, size, color)
    buf = BytesIO()
    image.save(buf, format='PNG')
    return buf.getvalue()


class RasterToWebpTests(SimpleTestCase):
    def test_converts_png_bytes(self):
        out = raster_to_webp_bytes(_png_bytes())
        self.assertIsNotNone(out)
        image = Image.open(BytesIO(out))
        self.assertEqual(image.format, 'WEBP')

    def test_skips_existing_webp(self):
        buf = BytesIO()
        Image.new('RGB', (8, 8), (1, 2, 3)).save(buf, format='WEBP')
        self.assertIsNone(raster_to_webp_bytes(buf.getvalue()))

    def test_keeps_alpha_as_rgba_webp(self):
        out = raster_to_webp_bytes(_png_bytes(mode='RGBA', color=(10, 20, 30, 0)))
        image = Image.open(BytesIO(out))
        self.assertEqual(image.mode, 'RGBA')

    def test_maybe_webp_renames_jpeg(self):
        buf = BytesIO()
        Image.new('RGB', (6, 6), (9, 9, 9)).save(buf, format='JPEG')
        upload = SimpleUploadedFile('cms/blocks/hero.jpg', buf.getvalue())
        name, content = maybe_webp_upload('cms/blocks/hero.jpg', upload)
        self.assertEqual(name, 'cms/blocks/hero.webp')
        self.assertTrue(content.name.endswith('.webp'))
        self.assertEqual(Image.open(content).format, 'WEBP')

    def test_skips_svg_name(self):
        raw = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        name, content = maybe_webp_upload('logo.svg', SimpleUploadedFile('logo.svg', raw))
        self.assertEqual(name, 'logo.svg')
        self.assertEqual(content.read(), raw)


class WebPStorageTests(SimpleTestCase):
    def test_save_writes_webp_filename(self):
        with TemporaryDirectory() as tmp:
            storage = WebPFileSystemStorage(location=tmp)
            name = storage.save(
                'cms/blocks/hero.png',
                ContentFile(_png_bytes(), name='hero.png'),
            )
            self.assertTrue(name.endswith('.webp'))
            stored = Path(tmp) / name
            self.assertTrue(stored.is_file())
            self.assertEqual(Image.open(stored).format, 'WEBP')


class ConvertStoredImageTests(SimpleTestCase):
    def test_converts_png_on_disk_and_keeps_original_until_caller_deletes(self):
        from django.core.files.storage import FileSystemStorage

        with TemporaryDirectory() as tmp:
            storage = FileSystemStorage(location=tmp)
            rel = 'cms/blocks/legacy.png'
            path = Path(tmp) / rel
            path.parent.mkdir(parents=True)
            path.write_bytes(_png_bytes())
            new_name = convert_stored_image(storage, rel)
            self.assertEqual(new_name, 'cms/blocks/legacy.webp')
            self.assertTrue((Path(tmp) / new_name).is_file())
            self.assertTrue(path.is_file())
            self.assertEqual(Image.open(Path(tmp) / new_name).format, 'WEBP')

    def test_dry_write_does_not_create_file(self):
        from django.core.files.storage import FileSystemStorage

        with TemporaryDirectory() as tmp:
            storage = FileSystemStorage(location=tmp)
            rel = 'cms/blocks/preview.jpg'
            path = Path(tmp) / rel
            path.parent.mkdir(parents=True)
            buf = BytesIO()
            Image.new('RGB', (6, 6), (9, 9, 9)).save(buf, format='JPEG')
            path.write_bytes(buf.getvalue())
            new_name = convert_stored_image(storage, rel, write=False)
            self.assertEqual(new_name, 'cms/blocks/preview.webp')
            self.assertFalse((Path(tmp) / new_name).exists())


class ConvertMediaCommandTests(TestCase):
    def test_rewrites_siteblock_png_to_webp(self):
        from apps.core.models import SiteBlock

        rel = 'cms/blocks/cmd-legacy.png'
        path = Path(settings.MEDIA_ROOT) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_png_bytes())
        block = SiteBlock.objects.create(page='home', key='cmd_webp_legacy')
        SiteBlock.objects.filter(pk=block.pk).update(image=rel)
        try:
            call_command('convert_media_webp')
            block.refresh_from_db()
            self.assertTrue(block.image.name.endswith('.webp'))
            self.assertFalse(path.exists())
            stored = Path(settings.MEDIA_ROOT) / block.image.name
            self.assertTrue(stored.is_file())
            self.assertEqual(Image.open(stored).format, 'WEBP')
        finally:
            leftover = Path(settings.MEDIA_ROOT) / (block.image.name or '')
            leftover.unlink(missing_ok=True)
            path.unlink(missing_ok=True)


