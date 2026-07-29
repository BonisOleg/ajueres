from django import template
from django.template.defaultfilters import linebreaks
from django.templatetags.static import static
from django.urls import translate_url
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import check_for_language

from apps.core.selectors import get_block_image, get_block_text

register = template.Library()

ADVANTAGE_IMAGES = {
    'assortment': 'img/advantages/assortment.png',
    'brands': 'img/advantages/brands.png',
    'logistics': 'img/advantages/logistics.png',
    'terms': 'img/advantages/terms.png',
    'experience': 'img/advantages/experience.png',
    'analytics': 'img/advantages/analytics.png',
}


@register.simple_tag(takes_context=True)
def change_language_url(context, lang_code):
    """Поточний URL з префіксом мови (для перемикачів RU/UZ/EN)."""
    request = context.get('request')
    if not request or not check_for_language(lang_code):
        return f'/{lang_code}/'
    translated = translate_url(request.get_full_path(), lang_code)
    return translated or f'/{lang_code}/'


@register.simple_tag
def block_text(blocks, key, default=''):
    return get_block_text(blocks or {}, key, default)


@register.simple_tag
def block_text_br(blocks, key, default=''):
    text = get_block_text(blocks or {}, key, default)
    return mark_safe(linebreaks(escape(text)))


@register.simple_tag
def block_image(blocks, key):
    return get_block_image(blocks or {}, key)


@register.filter(needs_autoescape=True)
def break_before_street(value, autoescape=True):
    """Перенос рядка перед «ул.» / street markers в адресі."""
    if value is None:
        return ''
    text = str(value)
    markers = (' ул.', ' ko‘cha', " ko'cha", ' st.', ' street')
    for marker in markers:
        idx = text.find(marker)
        if idx == -1:
            continue
        left = text[:idx].rstrip(' ,')
        right = text[idx + 1 :].lstrip()
        if autoescape:
            left = escape(left)
            right = escape(right)
        return mark_safe(f'{left},<br>{right}')
    return escape(text) if autoescape else text


@register.simple_tag
def advantage_icon(icon_key):
    key = icon_key or 'assortment'
    path = ADVANTAGE_IMAGES.get(key, ADVANTAGE_IMAGES['assortment'])
    url = escape(static(path))
    return mark_safe(
        f'<img src="{url}" alt="" width="184" height="184" '
        f'loading="lazy" decoding="async">'
    )
