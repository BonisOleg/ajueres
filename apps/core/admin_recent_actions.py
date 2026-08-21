"""Dedicated admin page for recent LogEntry actions (sidebar link)."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.template.response import TemplateResponse
from django.urls import path

RECENT_ACTIONS_LIMIT = 50


def recent_actions_view(request):
    admin_log = (
        LogEntry.objects.filter(user_id=request.user.pk)
        .select_related('content_type')
        .order_by('-action_time')[:RECENT_ACTIONS_LIMIT]
    )
    context = {
        **admin.site.each_context(request),
        'title': 'Последние действия',
        'subtitle': None,
        'admin_log': admin_log,
        'has_permission': True,
    }
    return TemplateResponse(request, 'admin/core/recent_actions.html', context)


def register_recent_actions_admin(site=None):
    site = site or admin.site
    if getattr(site, '_ajeres_recent_actions_urls', False):
        return
    site._ajeres_recent_actions_urls = True
    original_get_urls = site.get_urls

    def get_urls():
        custom = [
            path(
                'recent-actions/',
                site.admin_view(recent_actions_view),
                name='recent_actions',
            ),
        ]
        return custom + original_get_urls()

    site.get_urls = get_urls
