"""Admin Russian UI + public default language helpers."""

from __future__ import annotations

from django.conf import settings
from django.utils import translation


class PreferDefaultLanguageMiddleware:
    """
    First visit without language cookie/session → force LANGUAGE_CODE (ru).
    Ignores browser Accept-Language so the site opens in Russian by default.
    Chosen language cookie still works afterwards.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.default = getattr(settings, 'LANGUAGE_CODE', 'ru') or 'ru'

    def __call__(self, request):
        if request.path.startswith('/admin'):
            return self.get_response(request)

        has_cookie = bool(request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME))
        has_session = False
        try:
            has_session = bool(request.session.get(translation.LANGUAGE_SESSION_KEY))
        except Exception:
            has_session = False

        if not has_cookie and not has_session:
            request.META['HTTP_ACCEPT_LANGUAGE'] = self.default

        return self.get_response(request)


class AdminForceRussianMiddleware:
    """
    Force Russian UI for /admin/* without changing public LANGUAGES / LANGUAGE_CODE.
    Restores previous language after the request (thread-local safety).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/admin'):
            return self.get_response(request)

        previous = translation.get_language()
        translation.activate('ru')
        request.LANGUAGE_CODE = 'ru'
        try:
            return self.get_response(request)
        finally:
            if previous:
                translation.activate(previous)
            else:
                translation.deactivate()
