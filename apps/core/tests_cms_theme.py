"""Registry integrity tests for CMS content sections."""

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.block_defaults import BLOCK_DEFAULTS
from apps.core.cms_proxy_models import SECTION_PROXY_MODELS
from apps.core.site_content_registry import CONTENT_SECTIONS, all_registry_block_keys
from apps.core.admin_utils import format_admin_save_error
from apps.core.theme_fields import fill_css_background, validate_fill_payload
from apps.core.theme_models import BlockStyle, SiteButtonStyle


class RegistryTests(SimpleTestCase):
    def test_unique_block_keys(self):
        keys = all_registry_block_keys()
        self.assertEqual(len(keys), len(set(keys)))

    def test_unique_admin_model_names(self):
        names = [s.admin_model_name for s in CONTENT_SECTIONS]
        self.assertEqual(len(names), len(set(names)))

    def test_visibility_keys_in_section_blocks(self):
        for section in CONTENT_SECTIONS:
            if not section.visibility_key:
                continue
            self.assertIn(
                (section.page_slug, section.visibility_key),
                section.blocks,
            )

    def test_proxy_models_match_sections(self):
        self.assertEqual(len(SECTION_PROXY_MODELS), len(CONTENT_SECTIONS))
        model_names = {m._meta.model_name for m, _, _ in SECTION_PROXY_MODELS}
        expected = {s.admin_model_name for s in CONTENT_SECTIONS}
        self.assertEqual(model_names, expected)


class ThemeValidationTests(SimpleTestCase):
    def test_format_admin_save_error(self):
        from django.core.exceptions import ValidationError

        self.assertIn(
            'слишком',
            format_admin_save_error(ValidationError('Файл слишком большой')),
        )
        self.assertIn(
            'bg_color',
            format_admin_save_error(ValidationError({'bg_color': ['Неверный Hex']})),
        )

    def test_gradient_requires_end(self):
        errors = validate_fill_payload(
            fill_type='gradient',
            gradient_start='#ff0000',
            gradient_end='',
            require_complete=True,
        )
        self.assertIn('gradient_end', errors)

    def test_solid_ok(self):
        errors = validate_fill_payload(
            fill_type='solid',
            solid_color='#ff5a36',
            require_complete=True,
        )
        self.assertEqual(errors, {})

    def test_site_default_gradient_matches_front(self):
        css = fill_css_background(
            fill_type='gradient',
            gradient_start='#ff7a52',
            gradient_end='#db3f1c',
            gradient_angle=145,
        )
        self.assertIn('#ff5a36 48%', css)


class ThemeSeedTests(TestCase):
    def test_ensure_defaults(self):
        buttons = SiteButtonStyle.ensure_defaults()
        self.assertEqual(len(buttons), 4)
        created = BlockStyle.ensure_defaults()
        self.assertGreaterEqual(BlockStyle.objects.count(), 19)
        self.assertGreaterEqual(created, 0)

    def test_button_reset_returns_site_default(self):
        SiteButtonStyle.ensure_defaults()
        obj = SiteButtonStyle.objects.get(role='primary')
        self.assertTrue(obj.is_site_default())
        obj.fill_type = 'solid'
        obj.solid_color = '#112233'
        obj.save()
        self.assertFalse(obj.is_site_default())
        obj.apply_site_default()
        obj.save()
        obj.refresh_from_db()
        self.assertTrue(obj.is_site_default())
        self.assertEqual(obj.fill_type, 'gradient')
        self.assertIn('#ff5a36', obj.as_css_background())

    def test_block_defaults_cover_registry(self):
        for page, key in all_registry_block_keys():
            if key.endswith('_image') or key.endswith('_visible'):
                continue
            self.assertIn((page, key), BLOCK_DEFAULTS)


class ButtonStyleAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'owner',
            'owner@ajeres.uz',
            'OldPass123!',
        )
        self.client.force_login(self.user)
        SiteButtonStyle.ensure_defaults()

    def test_change_form_has_wheel_and_preview(self):
        obj = SiteButtonStyle.objects.get(role='secondary')
        response = self.client.get(
            reverse('admin:core_sitebuttonstyle_change', args=[obj.pk])
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('hex-color-wheel', content)
        self.assertIn('button-style-preview', content)
        self.assertIn('reset-to-site-default', content)
        self.assertIn('data-button-preview', content)
        self.assertIn('js/admin/button_style_preview.js', content)

    def test_reset_action_restores_default(self):
        obj = SiteButtonStyle.objects.get(role='primary')
        obj.fill_type = 'solid'
        obj.solid_color = '#000000'
        obj.save()
        response = self.client.get(
            reverse(
                'admin:core_sitebuttonstyle_reset_to_site_default',
                args=[obj.pk],
            )
        )
        self.assertEqual(response.status_code, 302)
        obj.refresh_from_db()
        self.assertTrue(obj.is_site_default())

    def test_staff_query_preview_overrides_css_without_save(self):
        obj = SiteButtonStyle.objects.get(role='primary')
        self.assertNotEqual(obj.solid_color.lower(), '#00ff00')
        response = self.client.get(
            reverse('home'),
            {
                'btn_preview': '1',
                'role': 'primary',
                'fill_type': 'solid',
                'solid_color': '#00ff00',
            },
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('--btn-primary-bg: #00ff00', content)
        self.assertIn('Попередній перегляд', content)
        obj.refresh_from_db()
        self.assertNotEqual(obj.solid_color.lower(), '#00ff00')

    def test_anonymous_cannot_preview_via_query(self):
        self.client.logout()
        response = self.client.get(
            reverse('home'),
            {
                'btn_preview': '1',
                'role': 'primary',
                'fill_type': 'solid',
                'solid_color': '#00ff00',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('--btn-primary-bg: #00ff00', response.content.decode())


_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
    b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
    b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)


class HeaderFooterCmsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            'owner',
            'owner@ajeres.uz',
            'OldPass123!',
        )
        self.client.force_login(self.user)

    def test_registry_has_header_footer(self):
        slugs = {(s.page_slug, s.slug) for s in CONTENT_SECTIONS}
        self.assertIn(('site', 'header'), slugs)
        self.assertIn(('site', 'footer'), slugs)

    def test_header_admin_has_labels_and_style(self):
        response = self.client.get(
            reverse('admin:core_siteheadersettings_changelist'),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('block__site__nav_home__text_html_ru', content)
        self.assertIn('style_bg_color', content)
        self.assertIn('style_bg_image', content)
        self.assertIn('accept="image/jpeg,image/png,image/webp,image/gif"', content)

    def test_footer_admin_has_texts(self):
        response = self.client.get(
            reverse('admin:core_sitefootersettings_changelist'),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('block__site__tagline__text_html_ru', content)
        self.assertNotIn('block__site__credit__', content)
        self.assertIn('style_bg_image', content)

    def test_home_uses_cms_nav_label(self):
        from apps.core.models import SiteBlock

        SiteBlock.objects.update_or_create(
            page='site',
            key='nav_home',
            defaults={
                'text_html': 'Головна-тест',
                'text_html_ru': 'Головна-тест',
            },
        )
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Головна-тест')

    def test_hero_image_preview_in_admin(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from apps.core.models import SiteBlock

        block, _ = SiteBlock.objects.get_or_create(page='home', key='hero_image')
        block.image.save(
            'hero-preview.png',
            SimpleUploadedFile('hero-preview.png', _PNG, content_type='image/png'),
            save=True,
        )
        response = self.client.get(
            reverse('admin:core_homeherosettings_changelist'),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, block.image.url)
        self.assertContains(response, 'accept="image/jpeg,image/png,image/webp,image/gif"')
        self.assertContains(response, 'admin-image-preview')

    def test_hero_empty_shows_static_fallback_preview(self):
        from apps.core.models import SiteBlock

        SiteBlock.objects.filter(page='home', key='hero_image').delete()
        response = self.client.get(
            reverse('admin:core_homeherosettings_changelist'),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('img/hero-samarkand.webp', content)
        self.assertIn('admin-image-preview', content)

    def test_home_uses_uploaded_hero_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        from apps.core.models import SiteBlock

        block, _ = SiteBlock.objects.get_or_create(page='home', key='hero_image')
        block.image.save(
            'hero-live.png',
            SimpleUploadedFile('hero-live.png', _PNG, content_type='image/png'),
            save=True,
        )
        response = self.client.get(reverse('home'))
        self.assertContains(response, block.image.url)

    def test_invalid_save_shows_error_text(self):
        change_url = reverse('admin:core_siteheadersettings_change', args=[1])
        self.client.get(
            reverse('admin:core_siteheadersettings_changelist'),
            follow=True,
        )
        response = self.client.post(
            change_url,
            {'style_bg_color': 'not-a-hex'},
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Не удалось сохранить', content)
        self.assertIn('Hex', content)

    def test_blockstyle_inline_includes_image(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        BlockStyle.ensure_defaults()
        style = BlockStyle.objects.get(page='site', section_key='header')
        style.bg_color = '#112233'
        style.bg_image.save(
            'header-bg.png',
            SimpleUploadedFile('header-bg.png', _PNG, content_type='image/png'),
            save=False,
        )
        style.save()
        css = style.section_inline_style()
        self.assertIn('background-color: #112233', css)
        self.assertIn('background-image: url(', css)
        self.assertIn('background-size: cover', css)
