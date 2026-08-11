"""Idempotent default superuser for local / Vercel demo."""

from __future__ import annotations

import os

from django.contrib.auth import get_user_model


def ensure_default_superuser() -> tuple[str, bool]:
    """
    Ensure staff superuser exists.
    Username/password from env (defaults: admin / admin).
    Returns (username, created).
    """
    username = (os.environ.get('DJANGO_SUPERUSER_USERNAME') or 'admin').strip()
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD') or 'admin'
    email = (os.environ.get('DJANGO_SUPERUSER_EMAIL') or 'admin@ajeres.uz').strip()

    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email},
    )
    user.email = email or user.email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()
    return username, created
