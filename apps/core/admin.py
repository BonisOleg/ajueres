"""Django admin for core: Unfold + CMS proxies + theme styles + i18n tabs."""

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.decorators import action
from unfold.enums import ActionVariant

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
            'Основной контент',
            {'fields': ('company_name', 'phone', 'email', 'address')},
        ),
        (
            'Стили и цвета',
            {
                'fields': ('accent_color', 'accent_ink', 'accent_soft'),
                'description': 'Глобальные акценты. Кнопки — в «Стили кнопок».',
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
    list_display = ('role', 'fill_type', 'swatch', 'is_default_display', 'gradient_angle')
    list_filter = ('fill_type',)
    ordering = ('role',)
    actions = ('reset_selected_to_site_default',)
    actions_detail = ('reset_to_site_default',)
    actions_row = ('reset_to_site_default',)
    change_form_before_template = 'admin/core/button_style_preview.html'

    fieldsets = (
        ('Роль', {'fields': ('role',)}),
        (
            'Стили и цвета',
            {
                'fields': (
                    'fill_type',
                    'solid_color',
                    'gradient_start',
                    'gradient_end',
                    'gradient_angle',
                ),
                'description': (
                    'Дефолт = вид кнопок на сайте. Однотонный — любое цветное колесо. '
                    '«Сбросить к виду сайта» откатывает правки.'
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return SiteButtonStyle.objects.count() < 4

    def has_delete_permission(self, request, obj=None):
        return False

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'solid_color':
            kwargs['widget'] = HexColorInputWidget(show_wheel=True)
        elif db_field.name in {'gradient_start', 'gradient_end'}:
            kwargs['widget'] = HexColorInputWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.display(description='Цвет')
    def swatch(self, obj):
        bg = obj.as_css_background(fallback='#ccc')
        return format_html(
            '<span style="display:inline-block;width:28px;height:28px;'
            'border-radius:50%;border:1px solid #c9c0b4;background:{};"></span>',
            bg,
        )

    @admin.display(description='Вид сайта', boolean=True)
    def is_default_display(self, obj):
        return obj.is_site_default()

    def changelist_view(self, request, extra_context=None):
        SiteButtonStyle.ensure_defaults()
        return super().changelist_view(request, extra_context)

    @admin.action(description='Сбросить к виду сайта')
    def reset_selected_to_site_default(self, request, queryset):
        count = 0
        for obj in queryset:
            obj.apply_site_default()
            obj.save()
            count += 1
        self.message_user(
            request,
            f'Сброшено к виду сайта: {count}',
            messages.SUCCESS,
        )

    @action(
        description='Сбросить к виду сайта',
        icon='restart_alt',
        url_path='reset-to-site-default',
        variant=ActionVariant.WARNING,
    )
    def reset_to_site_default(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj is None:
            self.message_user(request, 'Стиль не найден.', messages.ERROR)
            return HttpResponseRedirect(
                reverse('admin:core_sitebuttonstyle_changelist')
            )
        obj.apply_site_default()
        obj.save()
        self.message_user(request, 'Стиль возвращён к виду сайта.', messages.SUCCESS)
        return HttpResponseRedirect(
            reverse('admin:core_sitebuttonstyle_change', args=[obj.pk])
        )


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
            'Основной контент',
            {'fields': ('page', 'section_key', 'label')},
        ),
        (
            'Стили и цвета',
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
