"""Default legal copy for privacy and public offer (RU / UZ / EN)."""

from apps.core.models import LegalDocument
from apps.core.requisites import REQUISITES_EN, REQUISITES_RU, REQUISITES_UZ, rows_from_pairs

REQUISITES_HINT_RU = rows_from_pairs(REQUISITES_RU)
REQUISITES_HINT_UZ = rows_from_pairs(REQUISITES_UZ)
REQUISITES_HINT_EN = rows_from_pairs(REQUISITES_EN)

PRIVACY_DEFAULTS = {
    'title': 'Политика конфиденциальности',
    'title_ru': 'Политика конфиденциальности',
    'title_uz': 'Maxfiylik siyosati',
    'title_en': 'Privacy policy',
    'body': (
        '1. Общие положения\n'
        'Настоящая Политика конфиденциальности описывает, как ООО «AJERES» '
        '(далее — «Компания») обрабатывает персональные данные посетителей '
        'сайта и лиц, направляющих обращения через форму обратной связи.\n\n'
        '2. Какие данные мы обрабатываем\n'
        'Мы можем получать имя, номер телефона, адрес электронной почты и текст '
        'сообщения, которые вы указываете добровольно. Технические данные '
        '(IP-адрес, тип браузера) могут обрабатываться для обеспечения работы сайта.\n\n'
        '3. Цели обработки\n'
        'Данные используются исключительно для ответа на обращение, организации '
        'сотрудничества и улучшения качества сервиса. Мы не продаём персональные '
        'данные третьим лицам.\n\n'
        '4. Передача третьим лицам\n'
        'Передача возможна только при наличии законных оснований: требование '
        'уполномоченного органа, исполнение договора с провайдером услуг '
        '(хостинг, почта) или ваше согласие.\n\n'
        '5. Срок хранения\n'
        'Данные хранятся не дольше, чем это необходимо для указанных целей, '
        'если иной срок не установлен законодательством Республики Узбекистан.\n\n'
        '6. Права субъекта данных\n'
        'Вы вправе запросить уточнение, удаление или ограничение обработки своих '
        'данных, направив обращение на контактный e-mail, указанный на сайте.\n\n'
        '7. Защита информации\n'
        'Компания принимает организационные и технические меры для защиты данных '
        'от несанкционированного доступа, изменения или раскрытия.\n\n'
        '8. Изменения политики\n'
        'Актуальная редакция публикуется на этой странице. Продолжая пользоваться '
        'сайтом, вы подтверждаете ознакомление с действующей политикой.'
    ),
    'body_uz': (
        '1. Umumiy qoidalar\n'
        'Ushbu Maxfiylik siyosati “AJERES” MChJ (keyingi o‘rinlarda — “Kompaniya”) '
        'sayt tashrifbuyuruvchilari va aloqa formasi orqali murojaat yuborgan '
        'shaxslarning shaxsiy ma’lumotlarini qanday qayta ishlashini tasvirlaydi.\n\n'
        '2. Qanday ma’lumotlar qayta ishlanadi\n'
        'Siz ixtiyoriy ko‘rsatgan ism, telefon raqami, elektron pochta manzili va '
        'xabar matnini olishimiz mumkin. Sayt ishlashi uchun texnik ma’lumotlar '
        '(IP-manzil, brauzer turi) ham qayta ishlanishi mumkin.\n\n'
        '3. Qayta ishlash maqsadlari\n'
        'Ma’lumotlar faqat murojaatga javob berish, hamkorlikni tashkil etish va '
        'xizmat sifatini yaxshilash uchun ishlatiladi. Shaxsiy ma’lumotlar uchinchi '
        'shaxslarga sotilmaydi.\n\n'
        '4. Uchinchi shaxslarga uzatish\n'
        'Uzatish faqat qonuniy asoslar bo‘lganda mumkin: vakolatli organning talabi, '
        'xizmat ko‘rsatuvchi (hosting, pochta) bilan shartnoma yoki sizning roziligingiz.\n\n'
        '5. Saqlash muddati\n'
        'Ma’lumotlar O‘zbekiston Respublikasi qonunchiligida boshqa muddat belgilangan '
        'bo‘lmasa, ko‘rsatilgan maqsadlar uchun zarur bo‘lgan muddatdan ortiq saqlanmaydi.\n\n'
        '6. Subyekt huquqlari\n'
        'Saytda ko‘rsatilgan e-pochta orqali ma’lumotlarni aniqlashtirish, o‘chirish '
        'yoki qayta ishlashni cheklashni so‘rashingiz mumkin.\n\n'
        '7. Axborotni himoya qilish\n'
        'Kompaniya ruxsatsiz kirish, o‘zgartirish yoki oshkor etilishining oldini olish '
        'uchun tashkiliy va texnik choralarni qo‘llaydi.\n\n'
        '8. Siyosat o‘zgarishi\n'
        'Joriy tahrir ushbu sahifada e’lon qilinadi. Saytdan foydalanishni davom ettirib, '
        'siz amaldagi siyosat bilan tanishganingizni tasdiqlaysiz.'
    ),
    'body_en': (
        '1. General\n'
        'This Privacy Policy describes how AJERES LLC (the “Company”) processes '
        'personal data of website visitors and people who send messages via the '
        'contact form.\n\n'
        '2. Data we process\n'
        'We may receive the name, phone number, email address and message text '
        'you provide voluntarily. Technical data (IP address, browser type) may '
        'be processed to keep the site running.\n\n'
        '3. Purposes\n'
        'Data is used only to respond to inquiries, arrange cooperation and '
        'improve the service. We do not sell personal data to third parties.\n\n'
        '4. Sharing\n'
        'Sharing is possible only on legal grounds: a request from an authorised '
        'body, a contract with a service provider (hosting, email) or your consent.\n\n'
        '5. Retention\n'
        'Data is stored no longer than needed for these purposes, unless a longer '
        'period is required by the laws of the Republic of Uzbekistan.\n\n'
        '6. Your rights\n'
        'You may request correction, deletion or restriction of processing by '
        'writing to the contact email published on the website.\n\n'
        '7. Security\n'
        'The Company applies organisational and technical measures to protect '
        'data from unauthorised access, alteration or disclosure.\n\n'
        '8. Changes\n'
        'The current version is published on this page. By continuing to use the '
        'site you confirm that you have read this policy.'
    ),
    'requisites': [],
    'requisites_ru': [],
    'requisites_uz': [],
    'requisites_en': [],
}
PRIVACY_DEFAULTS['body_ru'] = PRIVACY_DEFAULTS['body']

OFFER_DEFAULTS = {
    'title': 'Публичная оферта',
    'title_ru': 'Публичная оферта',
    'title_uz': 'Ommaviy oferta',
    'title_en': 'Public offer',
    'body': (
        '1. Общие положения\n'
        'Настоящий документ является публичной офертой ООО «AJERES» (далее — '
        '«Исполнитель») в адрес любого заинтересованного лица (далее — «Заказчик») '
        'заключить договор на условиях, изложенных ниже. Акцептом оферты считается '
        'направление заявки через сайт и/или иное согласованное подтверждение.\n\n'
        '2. Предмет\n'
        'Исполнитель оказывает услуги дистрибуции продуктов питания: поставка, '
        'логистика, развитие брендов и сопутствующее сопровождение на территории '
        'Республики Узбекистан — в объёме, согласованном сторонами.\n\n'
        '3. Порядок взаимодействия\n'
        'Существенные условия конкретной поставки или услуги (ассортимент, объём, '
        'цена, сроки) согласовываются отдельно. Переписка и заявка с сайта могут '
        'использоваться как подтверждение намерения сотрудничать.\n\n'
        '4. Оплата и расчёты\n'
        'Порядок оплаты определяется договором или счётом. Реквизиты Исполнителя '
        'указываются в блоке «Реквизиты» на этой странице и/или в выставляемых '
        'документах.\n\n'
        '5. Ответственность\n'
        'Стороны несут ответственность в пределах, установленных законодательством '
        'Республики Узбекистан и согласованными документами. Исполнитель не отвечает '
        'за сбои связи и действия третьих лиц вне его контроля.\n\n'
        '6. Персональные данные\n'
        'Обработка данных Заказчика осуществляется в соответствии с Политикой '
        'конфиденциальности, размещённой на сайте.\n\n'
        '7. Срок действия и изменение оферты\n'
        'Оферта действует с момента публикации. Исполнитель вправе обновить текст; '
        'актуальная редакция всегда доступна на этой странице.\n\n'
        '8. Применимое право\n'
        'К отношениям сторон применяется право Республики Узбекистан. Споры '
        'разрешаются путём переговоров, а при недостижении согласия — в порядке, '
        'предусмотренном законодательством.\n\n'
        'Документ носит информационный характер и может быть уточнён сторонами '
        'в индивидуальном договоре.'
    ),
    'body_uz': (
        '1. Umumiy qoidalar\n'
        'Ushbu hujjat “AJERES” MChJ (keyingi o‘rinlarda — “Ijrochi”) tomonidan '
        'har qanday manfaatdor shaxs (keyingi o‘rinlarda — “Buyurtmachi”) bilan '
        'quyidagi shartlarda shartnoma tuzishga oid ommaviy ofertadir. Ofertani '
        'qabul qilish sayt orqali ariza yuborish va/yoki boshqa kelishilgan '
        'tasdiq hisoblanadi.\n\n'
        '2. Predmet\n'
        'Ijrochi oziq-ovqat mahsulotlarini distribyutsiya qilish: yetkazib berish, '
        'logistika, brendlarni rivojlantirish va O‘zbekiston Respublikasi '
        'hududida kelishilgan hajmdagi qo‘shimcha xizmatlarni ko‘rsatadi.\n\n'
        '3. Hamkorlik tartibi\n'
        'Muayyan yetkazib berish yoki xizmatning muhim shartlari (assortiment, '
        'hajm, narx, muddatlar) alohida kelishiladi. Yozishmalar va sayt arizasi '
        'hamkorlik niyatini tasdiqlash sifatida ishlatilishi mumkin.\n\n'
        '4. To‘lov\n'
        'To‘lov tartibi shartnoma yoki hisob-fakturada belgilanadi. Ijrochining '
        'rekvizitlari ushbu sahifadagi “Rekvizitlar” blokida va/yoki hisob '
        'hujjatlarida ko‘rsatiladi.\n\n'
        '5. Javobgarlik\n'
        'Tomonlar O‘zbekiston Respublikasi qonunchiligi va kelishilgan hujjatlar '
        'doirasida javobgar. Ijrochi aloqa uzilishlari va o‘z nazoratidan tashqari '
        'uchinchi shaxslar harakatlari uchun javobgar emas.\n\n'
        '6. Shaxsiy ma’lumotlar\n'
        'Buyurtmachi ma’lumotlari saytdagi Maxfiylik siyosatiga muvofiq qayta '
        'ishlanadi.\n\n'
        '7. Amal qilish muddati\n'
        'Oferta e’lon qilingan paytdan amal qiladi. Ijrochi matnni yangilashi '
        'mumkin; joriy tahrir doimo ushbu sahifada mavjud.\n\n'
        '8. Qo‘llaniladigan huquq\n'
        'Tomonlar munosabatlariga O‘zbekiston Respublikasi huquqi qo‘llaniladi. '
        'Nizolar muzokaralar yo‘li bilan, kelishuv bo‘lmasa — qonunda belgilangan '
        'tartibda hal etiladi.\n\n'
        'Hujjat axborot xususiyatiga ega va tomonlarning individual shartnomasida '
        'aniqlashtirilishi mumkin.'
    ),
    'body_en': (
        '1. General\n'
        'This document is a public offer by AJERES LLC (the “Contractor”) to any '
        'interested party (the “Customer”) to enter into an agreement on the terms '
        'below. Sending a request via the website and/or another agreed confirmation '
        'constitutes acceptance of the offer.\n\n'
        '2. Subject\n'
        'The Contractor provides food distribution services: supply, logistics, '
        'brand development and related support in the Republic of Uzbekistan, '
        'in the scope agreed by the parties.\n\n'
        '3. Cooperation\n'
        'Material terms of a specific supply or service (range, volume, price, '
        'timelines) are agreed separately. Correspondence and a website request '
        'may confirm the intention to cooperate.\n\n'
        '4. Payment\n'
        'Payment terms are set in a contract or invoice. The Contractor’s details '
        'are shown in the “Requisites” block on this page and/or in issued documents.\n\n'
        '5. Liability\n'
        'The parties are liable within the limits of the laws of the Republic of '
        'Uzbekistan and agreed documents. The Contractor is not liable for '
        'communication failures or third-party acts beyond its control.\n\n'
        '6. Personal data\n'
        'Customer data is processed in accordance with the Privacy Policy on the site.\n\n'
        '7. Term and changes\n'
        'The offer is effective from publication. The Contractor may update the text; '
        'the current version is always available on this page.\n\n'
        '8. Governing law\n'
        'The laws of the Republic of Uzbekistan apply. Disputes are resolved by '
        'negotiation and, failing agreement, as provided by law.\n\n'
        'This document is informational and may be refined in an individual contract.'
    ),
    'requisites': REQUISITES_HINT_RU,
    'requisites_ru': REQUISITES_HINT_RU,
    'requisites_uz': REQUISITES_HINT_UZ,
    'requisites_en': REQUISITES_HINT_EN,
}
OFFER_DEFAULTS['body_ru'] = OFFER_DEFAULTS['body']

LEGAL_FALLBACK_TITLES = {
    'privacy': {
        'ru': 'Политика конфиденциальности',
        'uz': 'Maxfiylik siyosati',
        'en': 'Privacy policy',
    },
    'offer': {
        'ru': 'Публичная оферта',
        'uz': 'Ommaviy oferta',
        'en': 'Public offer',
    },
}


def legal_fallback_title(slug: str, lang: str) -> str:
    fallbacks = LEGAL_FALLBACK_TITLES[slug]
    code = (lang or 'ru')[:2]
    return fallbacks.get(code) or fallbacks['ru']


def legal_display_title(slug: str, lang: str, document=None) -> str:
    if document is not None and (document.title or '').strip():
        return document.title.strip()
    return legal_fallback_title(slug, lang)

_TRANSLATED_FIELDS = (
    'title',
    'title_ru',
    'title_uz',
    'title_en',
    'body',
    'body_ru',
    'body_uz',
    'body_en',
    'requisites',
    'requisites_ru',
    'requisites_uz',
    'requisites_en',
)


_STALE_PRIVACY_TITLES = frozenset({'Политика приватности'})
_STALE_PRIVACY_BODY_MARKERS = (
    'ООО «AJERES» обрабатывает персональные данные из формы обратной связи',
    'ООО «AJERES» обрабатывает персональные данные, переданные',
    'AJERES LLC processes contact-form personal data',
    '"AJERES" MChJ aloqa formasidagi shaxsiy ma’lumotlarni faqat murojaatga',
)


def _is_blank_or_stale(slug: str, key: str, current) -> bool:
    if key.startswith('requisites'):
        from apps.core.requisites import normalize_requisites

        return not normalize_requisites(current)
    text = '' if current is None else str(current).strip()
    if not text:
        return True
    if slug != 'privacy':
        return False
    if key.startswith('title') and text in _STALE_PRIVACY_TITLES:
        return True
    if key.startswith('body') and any(text.startswith(m) for m in _STALE_PRIVACY_BODY_MARKERS):
        return True
    return False


def ensure_legal_document(slug: str, defaults: dict) -> tuple[LegalDocument, bool]:
    """Create legal copy if missing; never overwrite existing editor text."""
    create_defaults = {
        key: defaults[key]
        for key in _TRANSLATED_FIELDS
        if key in defaults
    }
    obj, created = LegalDocument.objects.get_or_create(
        slug=slug,
        defaults=create_defaults,
    )
    if created:
        return obj, True
    changed = False
    for key in _TRANSLATED_FIELDS:
        if key not in defaults:
            continue
        current = getattr(obj, key, None)
        if _is_blank_or_stale(slug, key, current):
            setattr(obj, key, defaults[key])
            changed = True
    if changed:
        obj.save()
    return obj, False
