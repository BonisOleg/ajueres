from modeltranslation.translator import TranslationOptions, register

from .models import Brand, Category, Product, ProductFilter


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ('name', 'short_description')


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'package', 'description')


@register(ProductFilter)
class ProductFilterTranslationOptions(TranslationOptions):
    fields = ('name',)
