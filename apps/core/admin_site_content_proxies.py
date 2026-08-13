"""Register Unfold CMS section proxy admins."""

from __future__ import annotations

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

from unfold.admin import ModelAdmin

from .admin_site_content import site_content_section_view
from .admin_utils import SingletonModelAdminMixin
from .cms_proxy_models import SECTION_PROXY_MODELS
from .models import SiteSettings


class SiteContentSectionAdmin(SingletonModelAdminMixin, ModelAdmin):
    page_slug: str = ''
    section_slug: str = ''

    def has_module_permission(self, request):
        return self.has_view_permission(request) or self.has_change_permission(request)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not self.has_change_permission(request):
            raise PermissionDenied
        return site_content_section_view(
            request,
            self.page_slug,
            self.section_slug,
            model_admin=self,
        )

    def changelist_view(self, request, extra_context=None):
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse(
                f'admin:core_{self.model._meta.model_name}_change',
                args=[obj.pk],
            )
        )


def register_site_content_section_admins(site=None):
    site = site or admin.site
    for model, page_slug, section_slug in SECTION_PROXY_MODELS:
        if site.is_registered(model):
            continue

        admin_class = type(
            f'{model.__name__}Admin',
            (SiteContentSectionAdmin,),
            {
                'page_slug': page_slug,
                'section_slug': section_slug,
            },
        )
        site.register(model, admin_class)
