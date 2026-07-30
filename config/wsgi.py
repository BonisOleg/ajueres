"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
# Vercel Python runtime looks for `app` or `application`.
app = application


def _bootstrap_vercel_sqlite() -> None:
    """Create /tmp SQLite + seed once per cold start (no DATABASE_URL)."""
    if os.environ.get('VERCEL') != '1':
        return
    db_url = os.environ.get('DATABASE_URL', '').strip()
    if db_url.startswith('postgres'):
        return

    db_path = Path('/tmp/ajeres.sqlite3')
    marker = Path('/tmp/ajeres.bootstrapped')
    if marker.exists() and db_path.exists() and db_path.stat().st_size > 0:
        return

    from django.core.management import call_command

    media = Path('/tmp/ajeres-media')
    media.mkdir(parents=True, exist_ok=True)
    call_command('migrate', interactive=False, verbosity=0)
    call_command('seed_site', verbosity=0)
    marker.write_text('ok', encoding='utf-8')


try:
    _bootstrap_vercel_sqlite()
except Exception:
    # Avoid crashing import-time detection; first request may retry.
    pass
