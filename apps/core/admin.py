from django.contrib import admin

from .models import (
    AboutSection,
    Advantage,
    CaseStudy,
    CompanyStat,
    LegalDocument,
    PartnerOffer,
    RetailPartner,
    SiteBlock,
    SiteSettings,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteBlock)
class SiteBlockAdmin(admin.ModelAdmin):
    list_display = ('page', 'key', 'has_image')
    list_filter = ('page',)
    search_fields = ('page', 'key', 'text_html')

    @admin.display(boolean=True, description='Зображення')
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(CompanyStat)
class CompanyStatAdmin(admin.ModelAdmin):
    list_display = ('value', 'label', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ('section_key', 'title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'section_key': ('title',)}


@admin.register(PartnerOffer)
class PartnerOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(RetailPartner)
class RetailPartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active', 'has_logo')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')

    @admin.display(boolean=True, description='Логотип')
    def has_logo(self, obj):
        return bool(obj.logo)


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'metric', 'order', 'is_active')
    list_editable = ('order', 'is_active')
