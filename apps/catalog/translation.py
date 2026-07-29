from modeltranslation.translator import TranslationOptions, register

from .models import Brand, Category, Product


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ('short_description',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'package', 'description')
