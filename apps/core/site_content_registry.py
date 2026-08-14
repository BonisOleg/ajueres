"""Registry of CMS content sections (proxy admin slots)."""

from __future__ import annotations

from dataclasses import dataclass, field

from django.urls import reverse_lazy

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
        slug='header',
        page_slug='site',
        title='Шапка сайта',
        sidebar_title='Шапка',
        sidebar_icon='web_asset',
        preview_url='/',
        style_section_key='header',
        blocks=(
            ('site', 'nav_home'),
            ('site', 'nav_catalog'),
            ('site', 'nav_about'),
            ('site', 'nav_contacts'),
            ('site', 'nav_mega_label'),
            ('site', 'nav_mega_all'),
            ('site', 'cta'),
            ('site', 'cta_mobile'),
            ('site', 'menu_label'),
            ('site', 'contacts_label'),
        ),
        field_groups=(
            FieldGroup(
                'Пункты меню',
                ('nav_home', 'nav_catalog', 'nav_about', 'nav_contacts'),
            ),
            FieldGroup(
                'Каталог и CTA',
                ('nav_mega_label', 'nav_mega_all', 'cta', 'cta_mobile'),
            ),
            FieldGroup(
                'Подписи меню',
                ('menu_label', 'contacts_label'),
            ),
        ),
        description=(
            'Подписи существующих пунктов и кнопки «Связаться». '
            'Новые кнопки добавить нельзя. Фон шапки — цвет или картинка ниже.'
        ),
    ),
    ContentSection(
        slug='footer',
        page_slug='site',
        title='Подвал сайта',
        sidebar_title='Подвал',
        sidebar_icon='vertical_align_bottom',
        preview_url='/',
        style_section_key='footer',
        blocks=(
            ('site', 'tagline'),
            ('site', 'copyright'),
            ('site', 'menu_label'),
            ('site', 'contacts_label'),
        ),
        field_groups=(
            FieldGroup('Тексты', ('tagline', 'copyright')),
            FieldGroup('Заголовки колонок', ('menu_label', 'contacts_label')),
        ),
        description=(
            'Существующие подписи подвала. Пункты меню берутся из «Шапки». '
            'Новые кнопки добавить нельзя. Строка «Разработано студией PrometeyLabs» '
            'зафиксирована в шаблоне и не редактируется. Фон — цвет или картинка ниже.'
        ),
    ),
    ContentSection(
        slug='hero',
        page_slug='home',
        title='Главная — Hero',
        sidebar_title='Hero',
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
            FieldGroup('Основной контент', ('hero_eyebrow', 'hero_title', 'hero_text', 'hero_cta')),
            FieldGroup('Медиафайлы', ('hero_image',)),
        ),
        description='Hero главной: тексты, CTA, изображение, видимость.',
    ),
    ContentSection(
        slug='advantages',
        page_slug='home',
        title='Главная — Преимущества',
        sidebar_title='Преимущества',
        sidebar_icon='star',
        preview_url='/',
        visibility_key='advantages_visible',
        style_section_key='advantages',
        blocks=(
            ('home', 'services_title'),
            ('home', 'advantages_visible'),
        ),
        field_groups=(FieldGroup('Основной контент', ('services_title',)),),
        description='Заголовок блока преимуществ. Карточки — пункт «Карточки преимуществ».',
    ),
    ContentSection(
        slug='brands',
        page_slug='home',
        title='Главная — Бренды',
        sidebar_title='Бренды',
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
            FieldGroup('Основной контент', ('brands_title', 'brands_subtitle')),
        ),
        description='Заголовки карусели брендов/партнёров.',
    ),
    ContentSection(
        slug='coop',
        page_slug='home',
        title='Главная — Сотрудничество',
        sidebar_title='Сотрудничество',
        sidebar_icon='handshake',
        preview_url='/',
        style_section_key='coop',
        blocks=(
            ('home', 'coop_title'),
            ('home', 'coop_eyebrow'),
            ('home', 'coop_cta'),
        ),
        field_groups=(
            FieldGroup('Основной контент', ('coop_title', 'coop_eyebrow', 'coop_cta')),
        ),
    ),
    ContentSection(
        slug='cta',
        page_slug='home',
        title='Главная — CTA',
        sidebar_title='CTA',
        sidebar_icon='campaign',
        preview_url='/',
        style_section_key='cta',
        blocks=(
            ('home', 'cta_title'),
            ('home', 'cta_text'),
        ),
        field_groups=(FieldGroup('Основной контент', ('cta_title', 'cta_text')),),
    ),
    ContentSection(
        slug='about',
        page_slug='about',
        title='О компании — Шапка',
        sidebar_title='Шапка',
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
            FieldGroup('Основной контент', ('eyebrow', 'title', 'intro', 'cta')),
            FieldGroup('Медиафайлы', ('side_image',)),
        ),
        description='Шапка /about. Секции текста — пункт «Секции».',
    ),
    ContentSection(
        slug='contacts',
        page_slug='contacts',
        title='Контакты — Тексты',
        sidebar_title='Тексты',
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
            FieldGroup('Основной контент', ('eyebrow', 'title', 'intro', 'partners_title')),
            FieldGroup(
                'Форма и контакты',
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


def cms_sidebar_item(page_slug: str, section_slug: str) -> dict:
    section = get_section(page_slug, section_slug)
    if section is None:
        raise ValueError(f'Unknown CMS section: {page_slug}/{section_slug}')
    return {
        'title': section.sidebar_title or section.title,
        'icon': section.sidebar_icon,
        'link': reverse_lazy(f'admin:core_{section.admin_model_name}_changelist'),
    }
