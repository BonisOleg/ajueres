"""Admin upload/text limits: compact Russian help_text and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.forms import ImageField
from django.utils.deconstruct import deconstructible

ALLOWED_IMAGE_EXT = frozenset({'.jpg', '.jpeg', '.png', '.webp', '.gif'})
MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 МБ — верхня межа одного файлу
MAX_WORD_DEFAULT = 28


@dataclass(frozen=True)
class ImageProfile:
    key: str
    max_bytes: int
    help_text: str
    error_too_big: str
    error_bad_type: str


@dataclass(frozen=True)
class TextLimit:
    max_chars: int
    help_text: str
    max_word: int = MAX_WORD_DEFAULT
    allow_newlines: bool = False


IMAGE_PROFILES: dict[str, ImageProfile] = {
    'hero': ImageProfile(
        key='hero',
        max_bytes=MAX_UPLOAD_BYTES,
        help_text=(
            'До 2 МБ, JPG/PNG/WebP. Лучше шире, чем выше '
            '(около 1600×900). Тяжёлый файл тормозит сайт.'
        ),
        error_too_big=(
            'Картинка больше 2 МБ. Сожмите её (качество 70–80%) '
            'или уменьшите размер и загрузите снова.'
        ),
        error_bad_type=(
            'Нужен файл JPG, PNG или WebP. PDF, Word и RAW не подойдут.'
        ),
    ),
    'photo': ImageProfile(
        key='photo',
        max_bytes=MAX_UPLOAD_BYTES,
        help_text=(
            'До 2 МБ, JPG/PNG/WebP. Для карточки лучше квадрат '
            'около 800×800. Слишком большое фото обрежется.'
        ),
        error_too_big=(
            'Фото больше 2 МБ. Уменьшите файл и загрузите снова — '
            'иначе страница будет долго открываться.'
        ),
        error_bad_type='Нужна картинка JPG, PNG или WebP. Этот файл не подходит.',
    ),
    'logo': ImageProfile(
        key='logo',
        max_bytes=400 * 1024,
        help_text=(
            'До 400 КБ, PNG или WebP, лучше квадрат. '
            'Большой логотип растянет блок партнёров.'
        ),
        error_too_big=(
            'Логотип больше 400 КБ. Сохраните его меньшего размера '
            'и загрузите снова.'
        ),
        error_bad_type='Логотип: только JPG, PNG или WebP.',
    ),
    'icon': ImageProfile(
        key='icon',
        max_bytes=200 * 1024,
        help_text='До 200 КБ, PNG/WebP, квадрат 64–256 px. Иначе иконка будет мыльной.',
        error_too_big='Иконка больше 200 КБ. Уменьшите файл и загрузите снова.',
        error_bad_type='Иконка: только JPG, PNG или WebP.',
    ),
    'background': ImageProfile(
        key='background',
        max_bytes=MAX_UPLOAD_BYTES,
        help_text=(
            'До 2 МБ, JPG/PNG/WebP, лучше 1920×1080. '
            'Тяжёлый фон замедлит весь сайт.'
        ),
        error_too_big=(
            'Фон больше 2 МБ. Сожмите картинку и загрузите снова.'
        ),
        error_bad_type='Фон: только JPG, PNG или WebP.',
    ),
}

IMAGE_FIELD_PROFILE: dict[str, str] = {
    'image': 'photo',
    'logo': 'logo',
    'icon': 'icon',
    'bg_image': 'background',
}

CMS_IMAGE_PROFILE: dict[str, str] = {
    'hero_image': 'hero',
    'side_image': 'photo',
}

IMAGE_ERROR_MESSAGES = {
    'invalid': 'Нужна картинка JPG, PNG или WebP. Этот файл не подходит.',
    'invalid_image': (
        'Файл повреждён или это не картинка. Откройте его в фоторедакторе, '
        'сохраните как JPG или PNG и загрузите снова.'
    ),
    'empty': 'Файл пустой. Выберите другое изображение.',
    'missing': 'Выберите файл.',
    'max_length': 'Слишком длинное имя файла. Переименуйте короче и загрузите снова.',
}

TEXT_LIMITS: dict[str, TextLimit] = {
    'hero_eyebrow': TextLimit(42, 'До 42 символов, одна строка. Длиннее — текст вылезет из шапки.'),
    'hero_title': TextLimit(72, 'До 72 символов, 1–2 строки. Длиннее — заголовок наложится на фото.'),
    'hero_text': TextLimit(
        220,
        'До 220 символов, 2–3 строки. Больше — блок станет слишком высоким.',
        allow_newlines=True,
    ),
    'hero_cta': TextLimit(22, 'До 22 символов. Длинная кнопка сломает ряд на телефоне.'),
    'services_title': TextLimit(48, 'До 48 символов, одна строка.'),
    'brands_title': TextLimit(40, 'До 40 символов, одна строка.'),
    'brands_subtitle': TextLimit(
        160,
        'До 160 символов, 1–2 строки.',
        allow_newlines=True,
    ),
    'coop_title': TextLimit(48, 'До 48 символов, одна строка.'),
    'coop_eyebrow': TextLimit(56, 'До 56 символов, одна строка.'),
    'coop_cta': TextLimit(24, 'До 24 символов — текст кнопки.'),
    'cta_title': TextLimit(48, 'До 48 символов, 1–2 строки.'),
    'cta_text': TextLimit(
        280,
        'До 280 символов, 3–4 строки. Дальше блок разъедется.',
        allow_newlines=True,
    ),
    'eyebrow': TextLimit(40, 'До 40 символов, одна короткая строка.'),
    'title': TextLimit(60, 'До 60 символов, 1–2 строки. Длиннее — заголовок вылезет за блок.'),
    'intro': TextLimit(
        420,
        'До 420 символов, 4–5 строк. Больше — колонка станет выше соседней.',
        allow_newlines=True,
    ),
    'cta': TextLimit(24, 'До 24 символов. Длинная кнопка не влезет на телефоне.'),
    'partners_title': TextLimit(40, 'До 40 символов, одна строка.'),
    'form_title': TextLimit(48, 'До 48 символов, одна строка.'),
    'form_lead': TextLimit(160, 'До 160 символов, 1–2 строки.', allow_newlines=True),
    'phone_note': TextLimit(36, 'До 36 символов, одна строка (часы работы).'),
    'email_note': TextLimit(40, 'До 40 символов, одна строка.'),
    'wholesale_title': TextLimit(40, 'До 40 символов.'),
    'wholesale_text': TextLimit(180, 'До 180 символов, 2 строки.', allow_newlines=True),
    'map_title': TextLimit(48, 'До 48 символов.'),
    'nav_home': TextLimit(16, 'До 16 символов. Длиннее — пункты меню налезут друг на друга.'),
    'nav_catalog': TextLimit(16, 'До 16 символов. В шапке места мало.'),
    'nav_about': TextLimit(18, 'До 18 символов. В шапке места мало.'),
    'nav_contacts': TextLimit(16, 'До 16 символов. В шапке места мало.'),
    'nav_mega_label': TextLimit(22, 'До 22 символов — подпись выпадающего меню.'),
    'nav_mega_all': TextLimit(28, 'До 28 символов.'),
    'cta_mobile': TextLimit(22, 'До 22 символов. Кнопка в мобильном меню.'),
    'tagline': TextLimit(140, 'До 140 символов, 2 строки в подвале.', allow_newlines=True),
    'copyright': TextLimit(48, 'До 48 символов, одна строка в подвале.'),
    'menu_label': TextLimit(20, 'До 20 символов — заголовок колонки в подвале.'),
    'contacts_label': TextLimit(24, 'До 24 символов — заголовок колонки в подвале.'),
    'company_name': TextLimit(36, 'До 36 символов. Длинное имя не влезет в шапку.'),
    'phone': TextLimit(24, 'До 24 символов. Только номер, без длинного комментария.'),
    'email': TextLimit(80, 'Обычный email, без пробелов.'),
    'address': TextLimit(180, 'До 180 символов, 2–3 строки адреса.', allow_newlines=True),
    'name': TextLimit(70, 'До 70 символов. Длиннее — название вылезет из карточки.'),
    'package': TextLimit(24, 'До 24 символов, напр. 235 гр. Длиннее — карточка поедет.'),
    'description': TextLimit(
        2000,
        'До 2000 символов. Текст на странице товара, короткие абзацы.',
        allow_newlines=True,
    ),
    'short_description': TextLimit(
        180,
        'До 180 символов, 2 строки.',
        allow_newlines=True,
    ),
    'text': TextLimit(220, 'До 220 символов, 2–3 строки.', allow_newlines=True),
    'body': TextLimit(
        8000,
        'Длинный текст страницы. Короткие абзацы читаются лучше.',
        allow_newlines=True,
        max_word=80,
    ),
    'requisites': TextLimit(2000, 'Реквизиты, по одному полю на строку.', allow_newlines=True),
    'value': TextLimit(12, 'До 12 символов (цифра или «200+»).'),
    'label': TextLimit(40, 'До 40 символов, одна строка под цифрой.'),
    'metric': TextLimit(32, 'До 32 символов.'),
}

UPLOAD_TOO_LARGE_REQUEST = (
    'Файл слишком большой для загрузки (больше 2 МБ). '
    'Сожмите картинку и попробуйте снова. '
    'Если грузите несколько фото сразу — загружайте по одному.'
)

SAVE_FILE_FAILED = (
    'Не удалось сохранить файл. Проверьте, что это картинка JPG/PNG/WebP '
    'не больше 2 МБ, имя без странных символов — и загрузите снова.'
)


def image_profile_for(field_name: str, cms_key: str = '') -> ImageProfile:
    profile_key = CMS_IMAGE_PROFILE.get(cms_key) or IMAGE_FIELD_PROFILE.get(
        _base_field_name(field_name),
        'photo',
    )
    return IMAGE_PROFILES[profile_key]


def text_limit_for(field_name: str, cms_key: str = '') -> TextLimit | None:
    return TEXT_LIMITS.get(cms_key) or TEXT_LIMITS.get(_base_field_name(field_name))


def _base_field_name(name: str) -> str:
    for lang in ('ru', 'uz', 'en'):
        suffix = f'_{lang}'
        if name.endswith(suffix):
            return name[: -len(suffix)]
    if name.startswith('text_html_'):
        return 'text_html'
    return name


def _file_size(upload) -> int:
    size = getattr(upload, 'size', None)
    if isinstance(size, int):
        return size
    return 0


def _suffix(upload) -> str:
    name = getattr(upload, 'name', '') or ''
    return Path(name).suffix.lower()


@deconstructible
class AdminImageUploadValidator:
    def __init__(self, profile_key: str = 'photo'):
        self.profile_key = profile_key

    def __call__(self, upload):
        if not upload or not isinstance(upload, UploadedFile):
            return
        profile = IMAGE_PROFILES[self.profile_key]
        suffix = _suffix(upload)
        if suffix and suffix not in ALLOWED_IMAGE_EXT:
            raise ValidationError(profile.error_bad_type)
        if _file_size(upload) > profile.max_bytes:
            raise ValidationError(profile.error_too_big)

    def __eq__(self, other):
        return (
            isinstance(other, AdminImageUploadValidator)
            and self.profile_key == other.profile_key
        )


def validate_admin_text(value: str, limit: TextLimit, label: str = '') -> None:
    text = value or ''
    if not text:
        return
    if not limit.allow_newlines and ('\n' in text or '\r' in text):
        raise ValidationError(
            'В этом поле нужна одна строка без переносов. Уберите Enter.'
        )
    length = len(text.strip())
    if length > limit.max_chars:
        raise ValidationError(
            f'Слишком длинно: {length} символов, можно до {limit.max_chars}. '
            'Сократите текст, иначе он вылезет за блок на сайте.'
        )
    longest = max((len(part) for part in text.replace('\n', ' ').split()), default=0)
    if longest > limit.max_word:
        raise ValidationError(
            f'Слово из {longest} букв без пробелов сломает вёрстку. '
            'Разбейте его пробелами или сократите.'
        )


def apply_image_guidelines(field, *, field_name: str = '', cms_key: str = '') -> None:
    profile = image_profile_for(field_name, cms_key)
    if field.help_text and str(field.help_text) not in profile.help_text:
        field.help_text = f'{field.help_text} {profile.help_text}'
    else:
        field.help_text = profile.help_text
    if isinstance(field, ImageField):
        field.error_messages = {**field.error_messages, **IMAGE_ERROR_MESSAGES}
    validators = [
        v
        for v in field.validators
        if not isinstance(v, AdminImageUploadValidator)
    ]
    validators.append(AdminImageUploadValidator(profile.key))
    field.validators = validators


def apply_text_guidelines(field, *, field_name: str = '', cms_key: str = '') -> None:
    limit = text_limit_for(field_name, cms_key)
    if limit is None:
        return
    if field.help_text and str(field.help_text) not in limit.help_text:
        field.help_text = f'{field.help_text} {limit.help_text}'
    else:
        field.help_text = limit.help_text
    if getattr(field, 'max_length', None) is None or field.max_length > limit.max_chars:
        field.max_length = limit.max_chars
    widget = getattr(field, 'widget', None)
    if widget is not None:
        widget.attrs['maxlength'] = str(limit.max_chars)
    field.validators = list(field.validators)

    def _check(value):
        validate_admin_text(value, limit)

    field.validators.append(_check)


def friendly_upload_exception(exc: BaseException) -> str | None:
    name = type(exc).__name__
    text = str(exc).lower()
    if name in {'RequestDataTooBig', 'TooManyFieldsSent'}:
        return UPLOAD_TOO_LARGE_REQUEST
    if name in {'SuspiciousFileOperation', 'SuspiciousOperation'}:
        return SAVE_FILE_FAILED
    if isinstance(exc, OSError) or 'cannot identify image' in text:
        return SAVE_FILE_FAILED
    if 'file is too large' in text or 'too large' in text:
        return UPLOAD_TOO_LARGE_REQUEST
    return None
