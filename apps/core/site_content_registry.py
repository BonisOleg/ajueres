"""Registry of CMS content sections (proxy admin slots)."""

from __future__ import annotations

from dataclasses import dataclass, field

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


@dataclass(frozen=True)
class FieldGroup:
    title: str
    keys: tuple[str, ...]


@dataclass(frozen=True)
class ContentSection:
    slug: str
    page_slug: str
    title: str
    blocks: tuple[tuple[str, str], ...]
    sidebar_title: str = ''
    sidebar_icon: str = 'edit_note'
    preview_url: str = '/'
    description: str = ''
    visibility_key: str = ''
    field_groups: tuple[FieldGroup, ...] = field(default_factory=tuple)
    admin_model_name: str = ''
    style_section_key: str = ''

    def __post_init__(self):
        if not self.admin_model_name:
            name = f'{self.page_slug}{self.slug}settings'.replace('_', '').lower()
            object.__setattr__(self, 'admin_model_name', name)
        if not self.sidebar_title:
            object.__setattr__(self, 'sidebar_title', self.title)


CONTENT_SECTIONS: tuple[ContentSection, ...] = (
    ContentSection(
        slug='hero',
        page_slug='home',
        title=str(_('Головна — Hero')),
        sidebar_icon='image',
        preview_url='/',
        visibility_key='hero_visible',
        style_section_key='hero',
        blocks=(
            ('home', 'hero_eyebrow'),
            ('home', 'hero_title'),
            ('home', 'hero_text'),
            ('home', 'hero_cta'),
            ('home', 'hero_image'),
            ('home', 'hero_visible'),
        ),
        field_groups=(
            FieldGroup('Основний контент', ('hero_eyebrow', 'hero_title', 'hero_text', 'hero_cta')),
            FieldGroup('Медіафайли', ('hero_image',)),
        ),
        description='Hero головної: тексти, CTA, зображення, видимість.',
    ),
    ContentSection(
        slug='advantages',
        page_slug='home',
        title=str(_('Головна — Переваги')),
        sidebar_icon='star',
        preview_url='/',
        visibility_key='advantages_visible',
        style_section_key='advantages',
        blocks=(
            ('home', 'services_title'),
            ('home', 'advantages_visible'),
        ),
        field_groups=(FieldGroup('Основний контент', ('services_title',)),),
        description='Заголовок блоку переваг. Картки — у розділі «Переваги».',
    ),
    ContentSection(
        slug='brands',
        page_slug='home',
        title=str(_('Головна — Бренди')),
        sidebar_icon='storefront',
        preview_url='/',
        visibility_key='brands_visible',
        style_section_key='brands',
        blocks=(
            ('home', 'brands_title'),
            ('home', 'brands_subtitle'),
            ('home', 'brands_visible'),
        ),
        field_groups=(
            FieldGroup('Основний контент', ('brands_title', 'brands_subtitle')),
        ),
        description='Заголовки каруселі брендів/партнерів.',
    ),
    ContentSection(
        slug='coop',
        page_slug='home',
        title=str(_('Головна — Співпраця')),
        sidebar_icon='handshake',
        preview_url='/',
        style_section_key='coop',
        blocks=(
            ('home', 'coop_title'),
            ('home', 'coop_eyebrow'),
            ('home', 'coop_cta'),
        ),
        field_groups=(
            FieldGroup('Основний контент', ('coop_title', 'coop_eyebrow', 'coop_cta')),
        ),
    ),
    ContentSection(
        slug='cta',
        page_slug='home',
        title=str(_('Головна — CTA')),
        sidebar_icon='campaign',
        preview_url='/',
        style_section_key='cta',
        blocks=(
            ('home', 'cta_title'),
            ('home', 'cta_text'),
        ),
        field_groups=(FieldGroup('Основний контент', ('cta_title', 'cta_text')),),
    ),
    ContentSection(
        slug='about',
        page_slug='about',
        title=str(_('Про компанію')),
        sidebar_icon='business',
        preview_url='/about/',
        style_section_key='intro',
        blocks=(
            ('about', 'eyebrow'),
            ('about', 'title'),
            ('about', 'intro'),
            ('about', 'cta'),
            ('about', 'side_image'),
        ),
        field_groups=(
            FieldGroup('Основний контент', ('eyebrow', 'title', 'intro', 'cta')),
            FieldGroup('Медіафайли', ('side_image',)),
        ),
        description='Шапка /about. Секції тексту — у «Секції Про компанію».',
    ),
    ContentSection(
        slug='contacts',
        page_slug='contacts',
        title=str(_('Контакти')),
        sidebar_icon='call',
        preview_url='/contacts/',
        style_section_key='intro',
        blocks=(
            ('contacts', 'eyebrow'),
            ('contacts', 'title'),
            ('contacts', 'intro'),
            ('contacts', 'partners_title'),
            ('contacts', 'form_title'),
            ('contacts', 'form_lead'),
            ('contacts', 'phone_note'),
            ('contacts', 'email_note'),
            ('contacts', 'wholesale_title'),
            ('contacts', 'wholesale_text'),
            ('contacts', 'map_title'),
        ),
        field_groups=(
            FieldGroup('Основний контент', ('eyebrow', 'title', 'intro', 'partners_title')),
            FieldGroup(
                'Форма та контакти',
                (
                    'form_title',
                    'form_lead',
                    'phone_note',
                    'email_note',
                    'wholesale_title',
                    'wholesale_text',
                    'map_title',
                ),
            ),
        ),
    ),
)


def get_section(page_slug: str, section_slug: str) -> ContentSection | None:
    for section in CONTENT_SECTIONS:
        if section.page_slug == page_slug and section.slug == section_slug:
            return section
    return None


def all_registry_block_keys() -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for section in CONTENT_SECTIONS:
        for pair in section.blocks:
            if pair not in seen:
                seen.add(pair)
                keys.append(pair)
    return keys


def build_content_sidebar_items() -> list[dict]:
    return [
        {
            'title': section.sidebar_title or section.title,
            'icon': section.sidebar_icon,
            'link': reverse_lazy(f'admin:core_{section.admin_model_name}_changelist'),
        }
        for section in CONTENT_SECTIONS
    ]
