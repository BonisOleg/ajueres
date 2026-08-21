from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import include, path

from apps.core.media_serve import serve_media
from apps.core.media_static import redirect_brand_logo, redirect_partner_logo
from apps.core.seo import robots_txt
from apps.core.sitemaps import SITEMAPS


def _strip_default_lang(request, subpath=''):
    target = f'/{subpath}' if subpath else '/'
    if not target.endswith('/'):
        target = f'{target}/'
    return redirect(target)


urlpatterns = [
    path('healthz/', lambda request: HttpResponse('ok', content_type='text/plain')),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='sitemap'),
    path('i18n/', include('django.conf.urls.i18n')),
    path(settings.ADMIN_URL, admin.site.urls),
    path('ru/', _strip_default_lang),
    path('ru/<path:subpath>', _strip_default_lang),
]

urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('products/', include('apps.catalog.urls')),
    path('contacts/', include('apps.leads.urls')),
    prefix_default_language=False,
)

urlpatterns += [
    path(
        'media/core/retail_partners/<str:filename>',
        redirect_partner_logo,
    ),
    path(
        'media/catalog/brands/<str:filename>',
        redirect_brand_logo,
    ),
]

if settings.DEBUG or getattr(settings, 'IS_VERCEL', False):
    urlpatterns += [
        path(
            'media/<path:path>',
            serve_media,
            name='serve_media',
        ),
    ]
