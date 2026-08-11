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
}

BLOCK_LABELS: dict[tuple[str, str], str] = {
    ('home', 'hero_visible'): 'Показувати Hero',
    ('home', 'advantages_visible'): 'Показувати переваги',
    ('home', 'brands_visible'): 'Показувати бренди',
    ('home', 'cases_visible'): 'Показувати кейси',
    ('home', 'hero_eyebrow'): 'Hero — eyebrow',
    ('home', 'hero_title'): 'Hero — заголовок',
    ('home', 'hero_text'): 'Hero — текст',
    ('home', 'hero_cta'): 'Hero — CTA',
    ('home', 'hero_image'): 'Hero — зображення',
    ('home', 'services_title'): 'Переваги — заголовок',
    ('home', 'brands_title'): 'Бренди — заголовок',
    ('home', 'brands_subtitle'): 'Бренди — підзаголовок',
    ('home', 'coop_title'): 'Співпраця — заголовок',
    ('home', 'coop_eyebrow'): 'Співпраця — eyebrow',
    ('home', 'coop_cta'): 'Співпраця — CTA',
    ('home', 'cta_title'): 'CTA — заголовок',
    ('home', 'cta_text'): 'CTA — текст',
    ('about', 'eyebrow'): 'Eyebrow',
    ('about', 'title'): 'Заголовок',
    ('about', 'intro'): 'Intro',
    ('about', 'cta'): 'CTA',
    ('about', 'side_image'): 'Бокове зображення',
    ('contacts', 'eyebrow'): 'Eyebrow',
    ('contacts', 'title'): 'Заголовок',
    ('contacts', 'intro'): 'Intro',
    ('contacts', 'partners_title'): 'Партнери — заголовок',
    ('contacts', 'form_title'): 'Форма — заголовок',
    ('contacts', 'form_lead'): 'Форма — лід',
    ('contacts', 'phone_note'): 'Нотатка телефону',
    ('contacts', 'email_note'): 'Нотатка email',
    ('contacts', 'wholesale_title'): 'Опт — заголовок',
    ('contacts', 'wholesale_text'): 'Опт — текст',
    ('contacts', 'map_title'): 'Карта — заголовок',
}

BLOCK_CONTENT_TYPES: dict[tuple[str, str], BlockType] = {
    ('home', 'hero_image'): 'image',
    ('about', 'side_image'): 'image',
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
    }
)


def is_visibility_key(key: str) -> bool:
    return key.endswith('_visible')


def block_type(page: str, key: str) -> BlockType:
    if is_visibility_key(key):
        return 'visibility'
    return BLOCK_CONTENT_TYPES.get((page, key), 'text')
