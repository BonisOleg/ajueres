"""Registry integrity tests for CMS content sections."""

from django.test import SimpleTestCase, TestCase

from apps.core.block_defaults import BLOCK_DEFAULTS
from apps.core.cms_proxy_models import SECTION_PROXY_MODELS
from apps.core.site_content_registry import CONTENT_SECTIONS, all_registry_block_keys
from apps.core.theme_fields import validate_fill_payload
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


class ThemeSeedTests(TestCase):
    def test_ensure_defaults(self):
        buttons = SiteButtonStyle.ensure_defaults()
        self.assertEqual(len(buttons), 4)
        created = BlockStyle.ensure_defaults()
        self.assertGreaterEqual(BlockStyle.objects.count(), 19)
        self.assertGreaterEqual(created, 0)

    def test_block_defaults_cover_registry(self):
        for page, key in all_registry_block_keys():
            if key.endswith('_image') or key.endswith('_visible'):
                continue
            self.assertIn((page, key), BLOCK_DEFAULTS)
