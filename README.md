# AJERES

Корпоративний сайт дистриб’ютора продуктів харчування (Узбекистан).

## Стек

- Backend: Django 5
- Frontend: HTML + CSS + HTMX + Vanilla JS (mobile-first)
- i18n: `ru` / `uz` / `en`
- Деплой: DigitalOcean Droplet (Docker + nginx + gunicorn + PostgreSQL)

## Швидкий старт (локально)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 manage.py migrate
python3 manage.py seed_site
python3 manage.py createsuperuser
python3 manage.py runserver
```

Сайт: http://127.0.0.1:8000/ru/  
Адмінка: `http://127.0.0.1:8000/<ADMIN_URL>/` (значення з `.env`, не `/admin/`)  
Healthcheck: http://127.0.0.1:8000/healthz/

## Структура URL

| Сторінка | Path |
| --- | --- |
| Головна | `/ru/` |
| Про компанію | `/ru/about/` |
| Каталог | `/ru/products/` |
| Контакти | `/ru/contacts/` |
| Privacy | `/ru/privacy/` |

Мови: префікс `/ru/`, `/uz/`, `/en/`.

## Docker (локально / Droplet HTTP)

```bash
cp .env.example .env
# обовʼязково: SECRET_KEY, POSTGRES_PASSWORD, ALLOWED_HOSTS
docker compose up -d --build
curl -sf http://127.0.0.1/healthz/
```

Сервіси: `web` (gunicorn), `nginx` (static/media + proxy), `db` (Postgres 16).

Static і media — Docker volumes (`static_volume`, `media_volume`); nginx віддає `/static/` і `/media/`.

## DigitalOcean Droplet (prod + SSL)

1. Клон репо на сервер → `/var/www/ajeres`
2. `cp .env.example .env` → заповнити `SECRET_KEY`, `POSTGRES_PASSWORD`, `ADMIN_URL`, `ALLOWED_HOSTS` (домен, IP, `web`, `127.0.0.1`, `localhost`)
3. HTTP: `docker compose up -d --build`
4. DNS A `@` / `www` → IP Droplet
5. Certbot на хості (`certonly --standalone`), потім у `deploy/nginx/docker.prod.conf` підставити шлях сертифіката
6. `.env`: `CSRF_TRUSTED_ORIGINS=https://...`, `SECURE_SSL_REDIRECT=False` (TLS термінує nginx)
7. Prod: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`
8. `docker compose exec web python3 manage.py createsuperuser`

Після оновлення коду: `docker compose ... up -d --build` — entrypoint робить `migrate` і `ensure_legal` (сторінки політики/оферти). Повний `seed_site` на проді не запускайте: він може перезаписати налаштування сайту.

Оновлення коду на сервері завжди з `--build` (інакше контейнер лишається на старому image).

## Контент з live-сайту

```bash
python3 manage.py import_live_content --force-texts
```

Імпортує каталог і зображення з https://ajeres.uz/catalog.html та тексти RU/UZ.
