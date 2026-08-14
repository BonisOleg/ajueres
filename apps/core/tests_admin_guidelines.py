from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.exceptions import RequestDataTooBig, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import ImageField
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

from apps.core.admin_guidelines import (
    AdminImageUploadValidator,
    apply_image_guidelines,
    apply_text_guidelines,
    friendly_upload_exception,
    validate_admin_text,
    TEXT_LIMITS,
)
from apps.core.admin_utils import format_admin_save_error as format_save


def _png(size=(8, 8)) -> bytes:
    buf = BytesIO()
    Image.new('RGB', size, (10, 20, 30)).save(buf, format='PNG')
    return buf.getvalue()


class GuidelineValidationTests(SimpleTestCase):
    def test_text_too_long(self):
        limit = TEXT_LIMITS['nav_home']
        with self.assertRaises(ValidationError) as ctx:
            validate_admin_text('x' * (limit.max_chars + 1), limit)
        self.assertIn('Сократите', str(ctx.exception))

    def test_long_word_breaks_layout(self):
        limit = TEXT_LIMITS['hero_title']
        with self.assertRaises(ValidationError) as ctx:
            validate_admin_text('A' * (limit.max_word + 1), limit)
        self.assertIn('пробел', str(ctx.exception))

    def test_image_too_big(self):
        upload = SimpleUploadedFile(
            'huge.png',
            b'0' * (2 * 1024 * 1024 + 10),
            content_type='image/png',
        )
        with self.assertRaises(ValidationError) as ctx:
            AdminImageUploadValidator('hero')(upload)
        self.assertIn('Сожмите', str(ctx.exception))

    def test_bad_extension(self):
        upload = SimpleUploadedFile('doc.pdf', b'%PDF', content_type='application/pdf')
        with self.assertRaises(ValidationError) as ctx:
            AdminImageUploadValidator('photo')(upload)
        self.assertIn('JPG', str(ctx.exception))

    def test_apply_image_help_and_errors(self):
        field = ImageField(required=False)
        apply_image_guidelines(field, field_name='logo')
        self.assertIn('400 КБ', field.help_text)
        self.assertIn('поврежд', field.error_messages['invalid_image'])

    def test_apply_text_maxlength(self):
        from django import forms

        field = forms.CharField(required=False)
        apply_text_guidelines(field, cms_key='hero_cta')
        self.assertEqual(field.max_length, 22)
        self.assertEqual(field.widget.attrs['maxlength'], '22')

    def test_request_too_big_is_friendly(self):
        self.assertIn('Сожмите', friendly_upload_exception(RequestDataTooBig()))
        self.assertIn('Сожмите', format_save(RequestDataTooBig()))


class CmsAdminGuidelineTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser('admin', 'a@a.a', 'pass')
        self.client.force_login(self.user)

    def test_hero_form_shows_russian_hints(self):
        response = self.client.get(
            reverse('admin:core_homeherosettings_changelist'),
            follow=True,
        )
        content = response.content.decode()
        self.assertIn('До 72 символов', content)
        self.assertIn('До 2 МБ', content)
        self.assertIn('admin-field-hint', content)

    def test_hero_rejects_long_title(self):
        url = reverse('admin:core_homeherosettings_change', args=[1])
        self.client.get(
            reverse('admin:core_homeherosettings_changelist'),
            follow=True,
        )
        response = self.client.post(
            url,
            {
                'block__home__hero_title__text_html_ru': 'Ж' * 80,
                'section_visible': 'on',
            },
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Не удалось сохранить', content)
        self.assertIn('Сократите', content)

    def test_product_image_hint(self):
        from apps.catalog.models import Brand, Category, Product

        brand = Brand.objects.create(slug='b', name='B')
        category = Category.objects.create(slug='c', name='C')
        product = Product.objects.create(
            brand=brand,
            category=category,
            slug='p',
            name='Товар',
            package='1 кг',
        )
        response = self.client.get(
            reverse('admin:catalog_product_change', args=[product.pk]),
        )
        self.assertContains(response, 'До 2 МБ')
        self.assertContains(response, 'До 70 символов')
