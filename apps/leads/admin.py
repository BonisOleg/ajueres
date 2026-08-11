from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(ModelAdmin):
    list_display = ('name', 'email', 'phone', 'language', 'status', 'created_at')
    list_filter = ('status', 'language', 'created_at')
    search_fields = ('name', 'email', 'phone', 'purpose')
    readonly_fields = (
        'purpose',
        'name',
        'phone',
        'email',
        'language',
        'ip_address',
        'created_at',
    )
    list_editable = ('status',)

    def has_add_permission(self, request):
        return False
