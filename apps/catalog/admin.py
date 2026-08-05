from django.contrib import admin

from .models import Brand, Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('parent', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    autocomplete_fields = ('parent',)


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'package', 'category', 'image', 'order', 'is_active')
    show_change_link = True


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_featured', 'is_active')
    list_editable = ('order', 'is_featured', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    inlines = (ProductInline,)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'package', 'order', 'is_active')
    list_filter = ('brand', 'category', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'package', 'brand__name', 'search_text')
    prepopulated_fields = {'slug': ('name', 'package')}
    autocomplete_fields = ('brand', 'category')
