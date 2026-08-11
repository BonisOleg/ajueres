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


def _bootstrap_vercel() -> None:
    """
    Vercel cold start:
    - without DATABASE_URL: migrate + seed ephemeral /tmp SQLite
    - always: ensure default superuser (admin/admin unless env overrides)
    """
    if os.environ.get('VERCEL') != '1':
        return

    from django.core.management import call_command

    from apps.core.ensure_superuser import ensure_default_superuser

    db_url = os.environ.get('DATABASE_URL', '').strip()
    if not db_url.startswith('postgres'):
        db_path = Path('/tmp/ajeres.sqlite3')
        marker = Path('/tmp/ajeres.bootstrapped')
        media = Path('/tmp/ajeres-media')
        media.mkdir(parents=True, exist_ok=True)

        needs_migrate = not (
            marker.exists() and db_path.exists() and db_path.stat().st_size > 0
        )
        if needs_migrate:
            call_command('migrate', interactive=False, verbosity=0)
            marker.write_text('ok', encoding='utf-8')

        # Always re-seed: idempotent, fills missing stats (e.g. 4th orb).
        call_command('seed_site', verbosity=0)
    else:
        # Managed Postgres: content seed is optional; admin must exist for /admin/.
        ensure_default_superuser()


try:
    _bootstrap_vercel()
except Exception:
    # Avoid crashing import-time detection; first request may retry.
    pass
