from io import BytesIO

from django.test import SimpleTestCase
from PIL import Image

from apps.catalog.image_utils import replace_dark_background


class ImageBackgroundTests(SimpleTestCase):
    def test_replaces_dark_uniform_background(self):
        im = Image.new('RGB', (40, 40), (42, 47, 51))
        im.paste(Image.new('RGB', (12, 20), (200, 30, 20)), (14, 10))
        buf = BytesIO()
        im.save(buf, format='PNG')

        out = replace_dark_background(buf.getvalue())
        result = Image.open(BytesIO(out)).convert('RGB')
        self.assertEqual(result.getpixel((0, 0)), (247, 247, 247))
        self.assertNotEqual(result.getpixel((20, 20)), (247, 247, 247))

    def test_keeps_already_light_background(self):
        im = Image.new('RGB', (20, 20), (250, 250, 250))
        buf = BytesIO()
        im.save(buf, format='PNG')
        raw = buf.getvalue()
        self.assertEqual(replace_dark_background(raw), raw)
