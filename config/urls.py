from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from apps.core.media_static import redirect_brand_logo, redirect_partner_logo

urlpatterns = [
    path('healthz/', lambda request: HttpResponse('ok', content_type='text/plain')),
    path('i18n/', include('django.conf.urls.i18n')),
    path(settings.ADMIN_URL, admin.site.urls),
]

urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('products/', include('apps.catalog.urls')),
    path('contacts/', include('apps.leads.urls')),
    prefix_default_language=True,
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
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
