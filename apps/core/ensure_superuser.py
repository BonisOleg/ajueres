"""Idempotent default superuser for local / Vercel demo."""

from __future__ import annotations

import os

from django.contrib.auth import get_user_model


def ensure_default_superuser() -> tuple[str, bool]:
    """
    Ensure staff superuser exists.
    Password from env only when creating a new user.
    Existing users keep the password set in admin.
    Returns (username, created).
    """
    username = (os.environ.get('DJANGO_SUPERUSER_USERNAME') or 'admin').strip()
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD') or 'admin'
    email = (os.environ.get('DJANGO_SUPERUSER_EMAIL') or 'admin@ajeres.uz').strip()

    User = get_user_model()
    user = User.objects.filter(username=username).first()
    if user is None:
        user = User(username=username, email=email)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        return username, True

    changed = False
    if email and user.email != email:
        user.email = email
        changed = True
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
    if not user.is_active:
        user.is_active = True
        changed = True
    if changed:
        user.save()
    return username, False
