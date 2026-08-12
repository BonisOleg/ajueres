from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html
from modeltranslation.admin import TranslationTabularInline
from unfold.admin import TabularInline

from apps.core.admin_utils import UnfoldTranslationAdmin

from .models import Brand, Category, Product, ProductFilter
from .product_filter_defaults import FILTER_SLUGS, filter_icon_static_path


@admin.register(Category)
class CategoryAdmin(UnfoldTranslationAdmin):
    list_display = ('name', 'slug', 'parent', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('parent', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    autocomplete_fields = ('parent',)


class ProductInline(TabularInline, TranslationTabularInline):
    model = Product
    extra = 0
    fields = ('name', 'package', 'category', 'image', 'order', 'is_active')
    show_change_link = True
    tab = True


@admin.register(Brand)
class BrandAdmin(UnfoldTranslationAdmin):
    list_display = ('name', 'slug', 'order', 'is_featured', 'is_active')
    list_editable = ('order', 'is_featured', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    inlines = (ProductInline,)


@admin.register(ProductFilter)
class ProductFilterAdmin(UnfoldTranslationAdmin):
    list_display = ('icon_preview', 'name', 'slug', 'order', 'is_active')
    list_display_links = ('name',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')

    @admin.display(description='Иконка')
    def icon_preview(self, obj):
        url = ''
        if obj.icon:
            try:
                url = obj.icon.url
            except ValueError:
                url = ''
        if not url and obj.slug in FILTER_SLUGS:
            url = static(filter_icon_static_path(obj.slug))
        if not url:
            return '—'
        return format_html(
            '<img src="{}" alt="" width="40" height="40" '
            'style="width:40px;height:40px;object-fit:contain;'
            'background:#111;border-radius:50%;">',
            url,
        )


@admin.register(Product)
class ProductAdmin(UnfoldTranslationAdmin):
    list_display = (
        'name',
        'brand',
        'category',
        'package',
        'extra_filters_preview',
        'order',
        'is_active',
    )
    list_filter = ('brand', 'category', 'is_active', 'extra_filters')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'package', 'brand__name', 'search_text')
    prepopulated_fields = {'slug': ('name', 'package')}
    autocomplete_fields = ('brand', 'category')
    list_select_related = ('brand', 'category')
    filter_horizontal = ('extra_filters',)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'brand',
                    'category',
                    'slug',
                    'name',
                    'package',
                    'description',
                    'image',
                    'order',
                    'is_active',
                ),
            },
        ),
        (
            'Дополнительные фильтры',
            {
                'fields': ('extra_filters',),
                'description': (
                    'Отметьте свойства — иконки появятся на карточке товара '
                    'и в фильтре каталога.'
                ),
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('extra_filters')

    @admin.display(description='Фильтры')
    def extra_filters_preview(self, obj):
        names = [item.name for item in obj.extra_filters.all()]
        return ', '.join(names) if names else '—'
