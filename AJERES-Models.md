# Логіка моделей БД — AJERES

**Версія:** 1.0 · **Стек:** Django + HTML/CSS + HTMX + Vanilla JS  
**Мови:** `ru` (default), `uz`, `en`  
**Референс каталогу:** https://ajeres.uz/catalog.html

---

## Рішення за уточненнями

| Питання | Рішення |
| --- | --- |
| Формат товару | Як на поточному сайті: картка з фото, назвою, фасуванням (напр. `235 гр.`) |
| Бренд ↔ товар | Завжди **1 бренд на товар** (`ForeignKey`, обов’язковий) |
| Контент сторінок | Повністю з адмінки (`SiteSettings` + `SiteBlock` + списки) |

---

## Apps

| App | Відповідальність |
| --- | --- |
| `core` | Singleton налаштувань, CMS-блоки сторінок, політика приватності |
| `catalog` | Category, Brand, Product |
| `leads` | Заявки з форми зворотного зв’язку |

**Не створюємо:** User/кабінет, Chat, Terms of Service, окремі Partner/Brand page models.

---

## ER (спрощено)

```
SiteSettings (pk=1)
SiteBlock (page, key) UNIQUE
LegalDocument (slug=privacy)

Category 1 ──< Product >── 1 Brand   (brand обов’язковий)

ContactInquiry  (ліди з форми)
```

Блок «Наші бренди» на `/` і під каталогом на `/products` = **один** queryset `Brand`.

---

## `catalog`

### Category
Фільтри каталогу за картою сайту.

| Поле | Тип | Примітка |
| --- | --- | --- |
| `slug` | SlugField unique | `sauces`, `noodles`, `seaweed`, `syrups`, `tea` |
| `name` | CharField + i18n | ru/uz/en |
| `image` | ImageField null | опційно для плитки категорії |
| `order` | PositiveInteger | сортування |
| `is_active` | Boolean | |

Seed (5 шт.): соуси/маринади, макаронні, водоростеві, сиропи, чай.

### Brand (= виробник)
Логотипи на головній і під каталогом. Як групи SenSoy / Chester на старому сайті.

| Поле | Тип | Примітка |
| --- | --- | --- |
| `slug` | SlugField unique | |
| `name` | CharField | бренд-нейм латиницею/як є (Sen Soy) |
| `logo` | ImageField | обов’язково для блоку логотипів |
| `short_description` | TextField + i18n, blank | короткий підпис |
| `order` | PositiveInteger | |
| `is_active` | Boolean | |
| `is_featured` | Boolean | пріоритет на головній |

### Product
Як на https://ajeres.uz/catalog.html — окрема картка SKU.

| Поле | Тип | Примітка |
| --- | --- | --- |
| `brand` | FK → Brand, PROTECT | **завжди 1**, required |
| `category` | FK → Category, PROTECT | для фільтра |
| `slug` | SlugField unique | |
| `name` | CharField + i18n | без дубля бренду в назві бажано: `Соус «Сладкий Чили»` |
| `package` | CharField + i18n | `235 гр.`, `1 л.`, `4,5 гр.` |
| `description` | TextField + i18n, blank | детальний опис |
| `image` | ImageField | фото картки |
| `order` | PositiveInteger | порядок у межах бренду/категорії |
| `is_active` | Boolean | |

Індекси: `(category, is_active)`, `(brand, is_active)`, пошук по `name_*`.

Відображення картки: `{brand.name} · {name} · {package}` або окремо в UI.

---

## `core` (CMS)

### SiteSettings (singleton `pk=1`)
Глобальне: контакти, бренд.

| Поле | Тип |
| --- | --- |
| `phone` | CharField |
| `email` | EmailField |
| `address` | TextField + i18n |
| `company_name` | CharField + i18n |

### SiteBlock
Тексти/фото/visibility секцій сторінок. Unique `(page, key)`.

| Поле | Тип |
| --- | --- |
| `page` | CharField | `home`, `about`, `products`, `contacts`, `privacy` |
| `key` | CharField | напр. `hero_title`, `hero_image`, `hero_visible` |
| `text_html` | TextField | текст або `'1'`/`'0'` для visibility |
| `image` | ImageField null | |

Секції через registry (адмінка «Вміст сторінок»), не хардкод у шаблонах.

**Приклади ключів:**

| page | keys (приклад) |
| --- | --- |
| `home` | hero_eyebrow, hero_title, hero_text, hero_cta, hero_image, advantages_visible, brands_visible, cases_visible |
| `about` | history_title, history_body, mission_*, vision_*, values_* |
| `contacts` | intro_title, intro_body, form_title, partners_section_title |
| `privacy` | title, body |

### List-моделі контенту (ListItem-шар)

| Модель | Де | Поля |
| --- | --- | --- |
| **Advantage** | головна — переваги | icon_key, title_*, text_*, order, is_active |
| **CompanyStat** | цифри / marquee | value, label_*, order, is_active |
| **AboutSection** | `/about` | section_key, title_*, body_*, order, is_active |
| **PartnerOffer** | блок партнерів на `/contacts` | title_*, text_*, order, is_active |
| **CaseStudy** | опційно головна | title_*, text_*, metric, order, is_active |

### LegalDocument
Лише політика приватності (`slug=privacy`), без Terms.

| Поле | Тип |
| --- | --- |
| `slug` | unique | `privacy` |
| `title` | + i18n |
| `body` | TextField + i18n |

---

## `leads`

### ContactInquiry

| Поле | Тип |
| --- | --- |
| `purpose` | TextField | «з якою метою» — вільний текст |
| `name` | CharField |
| `phone` | CharField |
| `email` | EmailField |
| `language` | CharField | `ru`/`uz`/`en` |
| `status` | CharField | `new` / `processed` |
| `created_at` | DateTime auto |
| `ip_address` | GenericIPAddress null | антиспам |

Немає FK на User.

---

## Що читає кожна сторінка

| URL | Джерела |
| --- | --- |
| `/` | SiteBlock(home) + Advantage + Brand + CompanyStat [+ CaseStudy] |
| `/about` | SiteBlock(about) + AboutSection + CompanyStat |
| `/products` | Category + Product (+ filter/search) → Brand знизу |
| `/contacts` | SiteSettings + SiteBlock(contacts) + PartnerOffer → POST ContactInquiry |
| privacy | LegalDocument |

---

## i18n

- `LANGUAGE_CODE = 'ru'`
- `LANGUAGES = [('ru',...), ('uz',...), ('en',...)]`
- Переклади полів: `django-modeltranslation` (або parler)
- Перемикач мов у header (вже в дизайні головної)

---

## Адмінка (напрям)

1. **Каталог** — звичайний ModelAdmin: Category, Brand, Product  
2. **Ліди** — ContactInquiry (readonly на сайті, статус в адмінці)  
3. **Вміст сторінок** — SiteSettings / SiteBlock через registry + proxy-секції (Unfold CMS pattern)  
4. ListItem-моделі — окремі пункти сайдбару

---

## Антипатерни (не робити)

1. Дві таблиці брендів для головної і каталогу  
2. M2M Product↔Brand  
3. Partner як auth-модель  
4. Хардкод текстів сторінок у шаблонах при «повністю з адмінки»  
5. Українська в `LANGUAGES`
