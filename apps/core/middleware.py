"""Admin-only language forcing (site languages stay untouched)."""

from __future__ import annotations

from django.utils import translation


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
