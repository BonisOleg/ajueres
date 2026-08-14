from urllib.parse import urlparse

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import translation

from .models import LegalDocument
from .seo import SITEMAP_URL_NAMES, _strip_default_lang_prefix, public_site_url


class StaticI18nSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def get_protocol(self, protocol=None):
        return urlparse(public_site_url()).scheme or 'https'

    def get_domain(self, site=None):
        return urlparse(public_site_url()).netloc

    def items(self):
        from django.conf import settings

        return [
            (lang, name)
            for lang, _label in settings.LANGUAGES
            for name in SITEMAP_URL_NAMES
        ]

    def location(self, item):
        lang, name = item
        with translation.override(lang):
            path = reverse(name)
        return _strip_default_lang_prefix(path, lang)

    def lastmod(self, item):
        _lang, name = item
        if name not in ('privacy', 'offer'):
            return None
        doc = LegalDocument.objects.filter(slug=name).only('updated_at').first()
        return getattr(doc, 'updated_at', None)


SITEMAPS = {'static': StaticI18nSitemap}
