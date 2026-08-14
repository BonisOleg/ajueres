"""CMS SiteBlock defaults, labels and content types for registry-driven admin."""

from __future__ import annotations

from typing import Literal

BlockType = Literal['text', 'image', 'visibility']

# (page, key) → default text_html (visibility: '1'/'0')
BLOCK_DEFAULTS: dict[tuple[str, str], str] = {
    ('home', 'hero_visible'): '1',
    ('home', 'advantages_visible'): '1',
    ('home', 'brands_visible'): '1',
    ('home', 'cases_visible'): '0',
    ('home', 'hero_eyebrow'): 'Дистрибьютор с 2018 года',
    ('home', 'hero_title'): 'Лучшие бренды в своем сегменте на рынке Узбекистана',
    (
        'home',
        'hero_text',
    ): (
        'Импорт, эксклюзивная дистрибуция, вывод на рынок Узбекистана '
        'новых производителей.'
    ),
    ('home', 'hero_cta'): 'Связаться с нами',
    ('home', 'services_title'): 'Наша деятельность',
    ('home', 'brands_title'): 'Наши партнёры',
    (
        'home',
        'brands_subtitle',
    ): (
        'Ритейл-партнёры и производители, с которыми мы развиваем '
        'ассортимент на рынке Узбекистана'
    ),
    ('home', 'coop_title'): 'Сотрудничество',
    ('home', 'coop_eyebrow'): 'Для торговых сетей, дистрибьюторов и HoReCa',
    ('home', 'coop_cta'): 'Стать партнером',
    ('home', 'cta_title'): 'Начнём сотрудничество?',
    (
        'home',
        'cta_text',
    ): (
        'Свяжитесь с нами в любое удобное время, профессиональная команда '
        'специалистов готова ответить на все вопросы и обсудить '
        'взаимовыгодное сотрудничество'
    ),
    ('about', 'eyebrow'): 'О компании',
    ('about', 'title'): 'ООО «AJERES»',
    (
        'about',
        'intro',
    ): (
        'Современная дистрибьюторская компания на рынке продуктов '
        'питания Республики Узбекистан. Специализируемся на выводе '
        'международных брендов и полном комплексе услуг: импорт, '
        'логистика, продажи, маркетинг и развитие брендов.'
    ),
    ('about', 'cta'): 'Связаться с нами',
    ('contacts', 'eyebrow'): 'Контакты',
    ('contacts', 'title'): 'Свяжитесь с нами',
    (
        'contacts',
        'intro',
    ): (
        'Команда ООО «AJERES» всегда открыта для новых партнерств и '
        'готова обсудить возможности сотрудничества.'
    ),
    ('contacts', 'partners_title'): 'Сотрудничество',
    ('contacts', 'form_title'): 'Отправить нам запрос',
    ('contacts', 'form_lead'): '',
    ('contacts', 'phone_note'): 'Пн–Сб, 9:00–18:00',
    ('contacts', 'email_note'): 'Отвечаем в течение дня',
    ('contacts', 'wholesale_title'): 'Оптовые поставки',
    (
        'contacts',
        'wholesale_text',
    ): 'Отгрузка со склада в Ташкенте и доставка по региону.',
    ('contacts', 'map_title'): 'Наш офис в Ташкенте',
    ('site', 'nav_home'): 'Главная',
    ('site', 'nav_catalog'): 'Каталог',
    ('site', 'nav_about'): 'О компании',
    ('site', 'nav_contacts'): 'Контакты',
    ('site', 'nav_mega_label'): 'Категории продуктов',
    ('site', 'nav_mega_all'): 'Смотреть весь каталог',
    ('site', 'cta'): 'Связаться',
    ('site', 'cta_mobile'): 'Связаться с нами',
    ('site', 'tagline'): 'Дистрибьютор продуктов питания в Республике Узбекистан',
    ('site', 'copyright'): 'Все права защищены.',
    ('site', 'menu_label'): 'Меню',
    ('site', 'contacts_label'): 'Контакты',
}

BLOCK_LABELS: dict[tuple[str, str], str] = {
    ('home', 'hero_visible'): 'Показывать Hero',
    ('home', 'advantages_visible'): 'Показывать преимущества',
    ('home', 'brands_visible'): 'Показывать бренды',
    ('home', 'cases_visible'): 'Показывать кейсы',
    ('home', 'hero_eyebrow'): 'Hero — eyebrow',
    ('home', 'hero_title'): 'Hero — заголовок',
    ('home', 'hero_text'): 'Hero — текст',
    ('home', 'hero_cta'): 'Hero — CTA',
    ('home', 'hero_image'): 'Hero — изображение',
    ('home', 'services_title'): 'Преимущества — заголовок',
    ('home', 'brands_title'): 'Бренды — заголовок',
    ('home', 'brands_subtitle'): 'Бренды — подзаголовок',
    ('home', 'coop_title'): 'Сотрудничество — заголовок',
    ('home', 'coop_eyebrow'): 'Сотрудничество — eyebrow',
    ('home', 'coop_cta'): 'Сотрудничество — CTA',
    ('home', 'cta_title'): 'CTA — заголовок',
    ('home', 'cta_text'): 'CTA — текст',
    ('about', 'eyebrow'): 'Eyebrow',
    ('about', 'title'): 'Заголовок',
    ('about', 'intro'): 'Intro',
    ('about', 'cta'): 'CTA',
    ('about', 'side_image'): 'Боковое изображение',
    ('contacts', 'eyebrow'): 'Eyebrow',
    ('contacts', 'title'): 'Заголовок',
    ('contacts', 'intro'): 'Intro',
    ('contacts', 'partners_title'): 'Партнёры — заголовок',
    ('contacts', 'form_title'): 'Форма — заголовок',
    ('contacts', 'form_lead'): 'Форма — лид',
    ('contacts', 'phone_note'): 'Заметка телефона',
    ('contacts', 'email_note'): 'Заметка email',
    ('contacts', 'wholesale_title'): 'Опт — заголовок',
    ('contacts', 'wholesale_text'): 'Опт — текст',
    ('contacts', 'map_title'): 'Карта — заголовок',
    ('site', 'nav_home'): 'Меню — Главная',
    ('site', 'nav_catalog'): 'Меню — Каталог',
    ('site', 'nav_about'): 'Меню — О компании',
    ('site', 'nav_contacts'): 'Меню — Контакты',
    ('site', 'nav_mega_label'): 'Мегаменю — заголовок',
    ('site', 'nav_mega_all'): 'Мегаменю — весь каталог',
    ('site', 'cta'): 'Кнопка «Связаться»',
    ('site', 'cta_mobile'): 'Кнопка в мобильном меню',
    ('site', 'tagline'): 'Подвал — описание',
    ('site', 'copyright'): 'Подвал — копирайт',
    ('site', 'menu_label'): 'Подвал — заголовок меню',
    ('site', 'contacts_label'): 'Подвал — заголовок контактов',
}

BLOCK_CONTENT_TYPES: dict[tuple[str, str], BlockType] = {
    ('home', 'hero_image'): 'image',
    ('about', 'side_image'): 'image',
}

# static path shown in admin (and on site) until a file is uploaded
IMAGE_FALLBACKS: dict[tuple[str, str], str] = {
    ('home', 'hero_image'): 'img/hero-samarkand.png',
}

INLINE_KEYS = frozenset(
    {
        'hero_eyebrow',
        'hero_cta',
        'services_title',
        'brands_title',
        'coop_title',
        'coop_eyebrow',
        'coop_cta',
        'cta_title',
        'eyebrow',
        'title',
        'cta',
        'partners_title',
        'form_title',
        'phone_note',
        'email_note',
        'wholesale_title',
        'map_title',
        'nav_home',
        'nav_catalog',
        'nav_about',
        'nav_contacts',
        'nav_mega_label',
        'nav_mega_all',
        'cta_mobile',
        'copyright',
        'menu_label',
        'contacts_label',
    }
)

MULTILINE_KEYS = frozenset(
    {
        'hero_text',
        'brands_subtitle',
        'cta_text',
        'intro',
        'form_lead',
        'wholesale_text',
        'tagline',
    }
)


LOCKED_CMS_BLOCKS = frozenset({('site', 'credit')})


def is_visibility_key(key: str) -> bool:
    return key.endswith('_visible')


def block_type(page: str, key: str) -> BlockType:
    if is_visibility_key(key):
        return 'visibility'
    return BLOCK_CONTENT_TYPES.get((page, key), 'text')
