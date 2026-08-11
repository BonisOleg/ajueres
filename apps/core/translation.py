from modeltranslation.translator import TranslationOptions, register

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


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ('company_name', 'address')


@register(SiteBlock)
class SiteBlockTranslationOptions(TranslationOptions):
    fields = ('text_html',)


@register(LegalDocument)
class LegalDocumentTranslationOptions(TranslationOptions):
    fields = ('title', 'body')


@register(Advantage)
class AdvantageTranslationOptions(TranslationOptions):
    fields = ('title', 'text')


@register(CompanyStat)
class CompanyStatTranslationOptions(TranslationOptions):
    fields = ('label',)


@register(AboutSection)
class AboutSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'body')


@register(PartnerOffer)
class PartnerOfferTranslationOptions(TranslationOptions):
    fields = ('title', 'text')


@register(RetailPartner)
class RetailPartnerTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(CaseStudy)
class CaseStudyTranslationOptions(TranslationOptions):
    fields = ('title', 'text', 'metric')
