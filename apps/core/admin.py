"""Django admin for core: Unfold + CMS proxies + theme styles + i18n tabs."""

from django.contrib import admin
from django.utils.html import format_html

from .admin_site_content_proxies import register_site_content_section_admins
from .admin_site_content_widgets import HexColorInputWidget
from .admin_utils import (
    ImagePreviewMixin,
    ReadableUnfoldFieldsMixin,
    SingletonModelAdminMixin,
    UnfoldTranslationAdmin,
)
from .models import (
    AboutSection,
    Advantage,
    BlockStyle,
    CaseStudy,
    CompanyStat,
    LegalDocument,
    PartnerOffer,
    RetailPartner,
    SiteButtonStyle,
    SiteSettings,
)
from unfold.admin import ModelAdmin


@admin.register(SiteSettings)
class SiteSettingsAdmin(
    ReadableUnfoldFieldsMixin,
    SingletonModelAdminMixin,
    UnfoldTranslationAdmin,
):
    fieldsets = (
        (
            'Основний контент',
            {'fields': ('company_name', 'phone', 'email', 'address')},
        ),
        (
            'Стилі та кольори',
            {
                'fields': ('accent_color', 'accent_ink', 'accent_soft'),
                'description': 'Глобальні акценти. Кнопки — у «Стилі кнопок».',
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in {'accent_color', 'accent_ink', 'accent_soft'}:
            kwargs['widget'] = HexColorInputWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        SiteButtonStyle.ensure_defaults()
        BlockStyle.ensure_defaults()
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(SiteButtonStyle)
class SiteButtonStyleAdmin(ReadableUnfoldFieldsMixin, ModelAdmin):
    list_display = ('role', 'fill_type', 'swatch', 'gradient_angle')
    list_filter = ('fill_type',)
    ordering = ('role',)

    fieldsets = (
        ('Роль', {'fields': ('role',)}),
        (
            'Стилі та кольори',
            {
                'fields': (
                    'fill_type',
                    'solid_color',
                    'gradient_start',
                    'gradient_end',
                    'gradient_angle',
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return SiteButtonStyle.objects.count() < 4

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in {'solid_color', 'gradient_start', 'gradient_end'}:
            kwargs['widget'] = HexColorInputWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description='Колір')
    def swatch(self, obj):
        bg = obj.as_css_background(fallback='#ccc')
        return format_html(
            '<span style="display:inline-block;width:48px;height:18px;'
            'border-radius:4px;border:1px solid #444;background:{};"></span>',
            bg,
        )

    def changelist_view(self, request, extra_context=None):
        SiteButtonStyle.ensure_defaults()
        return super().changelist_view(request, extra_context)


@admin.register(BlockStyle)
class BlockStyleAdmin(ReadableUnfoldFieldsMixin, ModelAdmin):
    list_display = (
        'label',
        'page',
        'section_key',
        'bg_color',
        'override_button_fill',
        'fill_type',
    )
    list_filter = ('page', 'override_button_fill', 'fill_type')
    search_fields = ('label', 'page', 'section_key')
    ordering = ('page', 'section_key')

    fieldsets = (
        (
            'Основний контент',
            {'fields': ('page', 'section_key', 'label')},
        ),
        (
            'Стилі та кольори',
            {
                'fields': (
                    'bg_color',
                    'override_button_fill',
                    'fill_type',
                    'solid_color',
                    'gradient_start',
                    'gradient_end',
                    'gradient_angle',
                ),
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in {
            'bg_color',
            'solid_color',
            'gradient_start',
            'gradient_end',
        }:
            kwargs['widget'] = HexColorInputWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def changelist_view(self, request, extra_context=None):
        BlockStyle.ensure_defaults()
        return super().changelist_view(request, extra_context)


@admin.register(LegalDocument)
class LegalDocumentAdmin(ReadableUnfoldFieldsMixin, UnfoldTranslationAdmin):
    list_display = ('slug', 'title', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Advantage)
class AdvantageAdmin(ReadableUnfoldFieldsMixin, UnfoldTranslationAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(CompanyStat)
class CompanyStatAdmin(ReadableUnfoldFieldsMixin, UnfoldTranslationAdmin):
    list_display = ('value', 'label', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(AboutSection)
class AboutSectionAdmin(ReadableUnfoldFieldsMixin, UnfoldTranslationAdmin):
    list_display = ('section_key', 'title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'section_key': ('title',)}


@admin.register(PartnerOffer)
class PartnerOfferAdmin(ReadableUnfoldFieldsMixin, UnfoldTranslationAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(RetailPartner)
class RetailPartnerAdmin(
    ImagePreviewMixin,
    ReadableUnfoldFieldsMixin,
    UnfoldTranslationAdmin,
):
    list_display = ('name', 'slug', 'order', 'is_active', 'get_image_preview')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    readonly_fields = ('get_image_preview',)
    preview_field = 'logo'


@admin.register(CaseStudy)
class CaseStudyAdmin(ReadableUnfoldFieldsMixin, UnfoldTranslationAdmin):
    list_display = ('title', 'metric', 'order', 'is_active')
    list_editable = ('order', 'is_active')


register_site_content_section_admins()
