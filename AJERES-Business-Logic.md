# Бізнес-логіка AJERES

**Версія:** 1.0  
**Стек:** Django views + services + HTMX + Vanilla JS  
**Мови:** `ru` (default) · `uz` · `en`  
**Принцип:** views тонкі; уся вибірка/фільтрація/валідація — у `services` / `selectors`.

---

## 1. Загальні правила

### 1.1. Активність (`is_active`)
На публічному сайті **завжди** тільки `is_active=True`.  
Неактивні записи видимі лише в адмінці.

### 1.2. Порядок (`order`, потім `id` / `name`)
Сортування списків: `order ASC`, далі стабільний ключ (`id` або `name`).

### 1.3. Мова
1. `LocaleMiddleware` визначає активну мову (`ru`/`uz`/`en`).
2. `modeltranslation` віддає поля `*_ru` / `*_uz` / `*_en` через звичайні атрибути (`obj.name`).
3. Fallback: `ru` → `en` → `uz` (як у settings).
4. Якщо переклад порожній — показуємо fallback, не ламаємо сторінку.

### 1.4. URL і мова
Рекомендовано: префікс мови `/ru/…`, `/uz/…`, `/en/…`  
(або cookie + `i18n_patterns`). Перемикач мов зберігає поточний path, змінює лише lang.

### 1.5. Кеш
| Ключ | Що | Інвалідація |
| --- | --- | --- |
| `site_settings` | SiteSettings pk=1 | save SiteSettings |
| `site_blocks:{lang}` | dict `(page,key)→block` | save SiteBlock |
| `brands_public` | список брендів для блоку | save Brand |
| `categories_public` | активні категорії | save Category |

Каталог товарів **не кешувати цілком** (залежить від filter/search) — лише короткоживучий fragment-cache за потреби.

### 1.6. Шари коду
```
View / HTMX endpoint
    → selectors (читання queryset)
    → services (записи, валідація, side-effects)
    → models
```

---

## 2. Селектори (читання)

### 2.1. `get_site_settings()`
- `SiteSettings.load()` (get_or_create pk=1)
- Кеш `site_settings`
- Використовується: header/footer, contacts, context processor

### 2.2. `get_blocks(page: str) → dict[str, SiteBlock]`
- Усі блоки `page=<page>`
- Повертає `{key: block}`
- Visibility: `block.text_html in ('1', 'true', 'yes')` для ключів `*_visible`
- Порожній/відсутній ключ → секція **схована** або fallback з seed (не 500)

### 2.3. `get_brands_for_showcase(*, featured_only: bool) → QuerySet[Brand]`
**Єдине джерело** для головної і під каталогом.

```
Brand.objects.filter(is_active=True)
  + if featured_only: filter(is_featured=True)   # головна
  + order_by('order', 'name')
```

| Місце | `featured_only` |
| --- | --- |
| Головна «Наши бренды» | `True` |
| Під каталогом на Products | `False` (усі активні) |

Якщо на головній `is_featured` усі `False` — показувати всі активні (fallback), щоб блок не був порожнім.

### 2.4. `get_categories() → QuerySet[Category]`
```
Category.objects.filter(is_active=True).order_by('order', 'name')
```
У фільтрі каталогу показувати **всі активні категорії**, навіть якщо зараз 0 товарів (UX: видно структуру).

### 2.5. `get_products(*, category_slug=None, brand_slug=None, q=None) → QuerySet[Product]`
База:
```
Product.objects
  .filter(is_active=True, brand__is_active=True, category__is_active=True)
  .select_related('brand', 'category')
```

Далі ланцюг фільтрів (AND):

| Параметр | Умова | Примітка |
| --- | --- | --- |
| `category` / `category_slug` | `category__slug=…` | з query string або path |
| `brand` / `brand_slug` | `brand__slug=…` | опційний другий фільтр |
| `q` | пошук (див. §3) | trim, min length |

Сортування: `brand__order`, `order`, `name`  
(як на старому сайті — візуально групи по бренду).

### 2.6. ListItem-селектори
```
Advantage / CompanyStat / AboutSection / PartnerOffer / CaseStudy:
  .filter(is_active=True).order_by('order', 'id')
```

### 2.7. `get_privacy_policy()`
```
LegalDocument.objects.filter(slug='privacy').first()
```
Немає запису → 404 або статичний fallback-шаблон (вирішити на імплементації: краще seed при деплої).

---

## 3. Пошук і фільтрація каталогу

### 3.1. Вхідні параметри (GET)
| Параметр | Тип | Приклад |
| --- | --- | --- |
| `category` | slug | `sauces` |
| `brand` | slug | `sen-soy` |
| `q` | string | `чили` |
| `page` | int ≥ 1 | `2` |

Невідомий slug категорії/бренду → **порожній список товарів** + flash/empty-state (не 500).  
Альтернатива: 404 — **не** рекомендується для filter UX.

Невалідний `page` (`abc`, `0`, від’ємне) → трактувати як `1`.  
`page` більший за останню сторінку → показати **останню** сторінку (не 404).

### 3.2. Нормалізація `q`
1. `strip()`
2. Схлопнути зайві пробіли
3. Якщо `len(q) < 2` → ігнорувати пошук (показати як без `q`)
4. Max length 100 (обрізати)

### 3.3. Алгоритм пошуку (v1)
`icontains` по поточному перекладу + назві бренду:

```
Q(name__icontains=q)
| Q(package__icontains=q)
| Q(description__icontains=q)
| Q(brand__name__icontains=q)
```

Мова: Django ORM з modeltranslation шукає в полі активної мови (`name` → `name_ru` тощо).  
Для надійності можна OR по `name_ru`, `name_uz`, `name_en` — **рекомендовано для B2B**, щоб запит російською знаходив товар і на uz-сторінці.

**Рішення v1 (затвердити):** пошук по **усіх трьох** мовних полях назви + `brand.name` + `package_*`.

### 3.4. Комбінації
```
category=sauces & q=чили  → соуси, де назва містить «чили»
brand=sen-soy & category=tea → порожньо (якщо немає таких SKU)
без параметрів → усі активні товари
```

### 3.5. Групування для UI
**Бізнес-рішення:**  
- Фільтр/чіпи — по **категорії** (карта).  
- Відображення списку — **групами по бренду** (звичний UX поточного каталогу).  
- При активному `category` — групи брендів лише з товарів цієї категорії.

**Важливо з пагінацією:** пагінуємо **товари (плоский queryset)**, потім групуємо лише товари **поточної сторінки**.  
Один бренд може розірватись між сторінками — це нормально (не пагінуємо «цілими брендами»).

Псевдокод:
```
products_qs = get_products(category_slug=..., brand_slug=..., q=...)
page_obj = paginate_products(products_qs, page=page, per_page=PER_PAGE)
grouped = OrderedDict()
for p in page_obj.object_list:
    grouped.setdefault(p.brand, []).append(p)
```

### 3.6. HTMX
- Зміна категорії / бренду / пошуку / сторінки → `GET` partial `#catalog-results`
- URL оновлювати через `history` (шаринг лінка з фільтром + `page`)
- Debounce пошуку: **300 ms** на клієнті
- Порожній результат → partial «Ничего не найдено» мовою UI
- Клік пагінації — HTMX swap того ж `#catalog-results` + `scroll:top` контейнера каталогу (не всієї сторінки)

### 3.7. Пагінація (обов’язково на Каталозі)

| Параметр | Значення |
| --- | --- |
| Query-параметр | `page` |
| Розмір сторінки | **24** товари (`CATALOG_PER_PAGE = 24`) |
| Движок | `django.core.paginator.Paginator` |
| Об’єкт пагінації | по **Product**, не по Brand |

#### Правила скидання сторінки
Зміна `category`, `brand` або `q` → **завжди скидати на `page=1`**  
(на клієнті при зміні фільтра не передавати старий `page`; на сервері — якщо прийшов `page` з новим фільтром, дозволено, але UX-кнопки фільтрів мають лінки без `page` або з `page=1`).

#### Збереження фільтрів у лінках пагінації
Кожне посилання «1, 2, 3… / prev / next» зберігає поточні `category`, `brand`, `q`:
```
/products?category=sauces&q=чили&page=2
```

#### UI пагінатора
Показувати, якщо `paginator.num_pages > 1`:
- Prev / Next (disabled на краях)
- Номери сторінок (вікно ±2 від поточної + перша/остання за потреби)
- Опційно короткий підпис: «Показано 1–24 из 86»

#### Селектор
```
def paginate_products(qs, *, page: int, per_page: int = 24) -> Page:
    paginator = Paginator(qs, per_page)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
```

---

## 4. Логіка по сторінках

### 4.1. Головна `/`
| Блок | Джерело | Умова показу |
| --- | --- | --- |
| Hero | `get_blocks('home')` | `hero_visible` |
| Переваги | `Advantage` | `advantages_visible` + є активні |
| Цифри / marquee | `CompanyStat` | є активні |
| Бренди | `get_brands_for_showcase(featured_only=True)` | `brands_visible` + є бренди |
| Кейси | `CaseStudy` | `cases_visible` + є активні |
| CTA | лінк на contacts | завжди в hero |

Контекст-процесор: settings + nav (статичні URL).

### 4.2. Про компанію `/about`
| Блок | Джерело |
| --- | --- |
| CMS intro | `get_blocks('about')` |
| Секції | `AboutSection` за `order` |
| Цифри | `CompanyStat` |

Секції з порожнім `body` після trim — **пропускати** у рендері.

### 4.3. Продукти `/products`
1. `categories = get_categories()`
2. Зчитати GET: `category`, `brand`, `q`, `page`
3. `products_qs = get_products(...)`
4. `page_obj = paginate_products(products_qs, page=page, per_page=24)`
5. `grouped = group_by_brand(page_obj.object_list)`
6. У контекст: `page_obj`, `paginator`, `grouped`, активні фільтри
7. `brands_showcase = get_brands_for_showcase(featured_only=False)` — блок **під** каталогом (поза пагінацією, завжди повний список)
8. Active chip: поточний `category` slug (або «Все»)

Клік по логотипу бренду в нижньому блоці (опційно v1.1):  
`?brand=<slug>&page=1` — фільтр каталогу вгору + scroll to results.

### 4.4. Контакти `/contacts`
| Блок | Джерело |
| --- | --- |
| Intro / заголовки | `get_blocks('contacts')` |
| Телефон, email, адреса | `get_site_settings()` |
| Партнерський блок | `PartnerOffer` |
| Форма | POST → `submit_contact_inquiry` |

### 4.5. Privacy
`get_privacy_policy()` → HTML/текст з адмінки.

---

## 5. Форма зворотного зв’язку (запис)

### 5.1. Поля (строго з карти)
1. `purpose` — текст, обов’язковий  
2. `name` — обов’язковий  
3. `phone` — обов’язковий  
4. `email` — обов’язковий, валідний email  

### 5.2. Валідація (`services.leads.submit_contact_inquiry`)
| Поле | Правила |
| --- | --- |
| purpose | strip; 3–2000 символів |
| name | strip; 2–255 |
| phone | strip; 5–64; дозволені `+`, цифри, пробіли, `-`, `()` |
| email | EmailValidator; lower() |
| honeypot | приховане поле `website` — якщо заповнене → silent success (антибот), **не** писати в БД |
| rate limit | ≤ 5 заявок / IP / годину → 429 або м’яке повідомлення |

### 5.3. Збереження
```
ContactInquiry.objects.create(
  purpose=..., name=..., phone=..., email=...,
  language=get_language(),  # ru|uz|en
  status=NEW,
  ip_address=client_ip,
)
```

### 5.4. Відповідь
- HTMX: partial success («Заявка отправлена»)
- Звичайний POST: redirect contacts + flash success
- **Не** відправляти email обов’язково в v1 (опційно сигнал/celery пізніше)
- Адмін міняє `status` → `processed`

### 5.5. Чого немає
Чат, кабінет, авторизація заявника — **немає**.

---

## 6. Навігація і глобальний контекст

Context processor `site_context`:
```
{
  settings: SiteSettings,
  current_language: ...,
  languages: [ru, uz, en],
  nav: [
    {url: home, label},
    {url: about, label},
    {url: products, label},
    {url: contacts, label},
  ]
}
```

Лейбли nav — з `django.po` / gettext (не з БД), або з SiteBlock `nav_*` якщо захочуть редагувати в адмінці (v1 — gettext).

---

## 7. Інваріанти і захист даних

| Правило | Реалізація |
| --- | --- |
| Не видаляти бренд/категорію з товарами | `on_delete=PROTECT` |
| Товар завжди з брендом | `brand` NOT NULL |
| Публічно лише активне | усі селектори з `is_active` |
| Не світити чужі ліди | ContactInquiry тільки admin |
| XSS у CMS | у шаблонах `|safe` лише для довіреного `text_html` з адмінки; user input форми — ніколи без escape |
| CSRF | усі POST з csrf_token (HTMX headers) |

---

## 8. Порожні стани (обов’язкові)

| Ситуація | UX |
| --- | --- |
| 0 товарів після фільтра | «Ничего не найдено» + кнопка «Сбросить» (пагінатор сховати) |
| 1 сторінка результатів | пагінатор сховати (`num_pages == 1`) |
| 0 брендів | сховати секцію брендів |
| 0 переваг | сховати секцію |
| Немає SiteBlock | не падати; порожній рядок / seed default |
| Немає privacy | 404 або заглушка з адмін-нагадуванням |

---

## 9. Потік даних (схема)

```
[Browser]
   │ GET /products?category=sauces&q=чили&page=2
   ▼
[products_view]
   │ parse & normalize query (category, brand, q, page)
   ▼
[selectors.get_products]
   │ filter is_active + category + search
   │ select_related brand, category
   ▼
[paginate_products]  ← 24 / page
   ▼
[group_by_brand]     ← лише object_list поточної сторінки
   ▼
[Template / HTMX partial]
   │ cards + pagination controls
   ▼
[Browser]

[Browser] POST /contacts/ (HTMX)
   ▼
[contacts_submit_view]
   ▼
[services.submit_contact_inquiry]  ← validate, honeypot, rate limit
   ▼
[ContactInquiry.create]
   ▼
[success partial]
```

---

## 10. Що реалізувати першим (порядок коду)

1. `apps/core/selectors.py` — settings, blocks  
2. `apps/catalog/selectors.py` — brands, categories, products, group_by_brand  
3. `apps/leads/services.py` — submit_contact_inquiry  
4. Views: home → products (filter + pagination + HTMX) → contacts → about  
5. Context processor + i18n URLs  
6. Seed: 5 categories, brands/products з поточного сайту, privacy stub  

---

## 11. Відкриті рішення (затверджено за замовчуванням)

| Тема | Default |
| --- | --- |
| Групування каталогу | по бренду + фільтр по категорії |
| Пошук | по всіх мовах name + brand.name + package |
| Featured brands на головній | `is_featured=True`, fallback = усі active |
| Пагінація каталогу | **так**, 24 товари/сторінка, параметр `page`; пагінація по Product, потім group by brand |
| Email при заявці | немає в v1 |
| Клік по логотипу бренду під каталогом | опційно v1.1 → `?brand=&page=1` |
