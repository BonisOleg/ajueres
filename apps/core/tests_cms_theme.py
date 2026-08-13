"""Registry integrity tests for CMS content sections."""

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.block_defaults import BLOCK_DEFAULTS
from apps.core.cms_proxy_models import SECTION_PROXY_MODELS
from apps.core.site_content_registry import CONTENT_SECTIONS, all_registry_block_keys
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
