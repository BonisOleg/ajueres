#!/usr/bin/env python3
"""Fill locale/*/LC_MESSAGES/django.po msgstr from translation maps."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EN = {
    "Главная": "Home",
    "Продукты": "Products",
    "Каталог": "Catalog",
    "О компании": "About",
    "Контакты": "Contacts",
    "Слишком много заявок. Попробуйте позже.": "Too many requests. Please try again later.",
    "Заявка отправлена. Мы свяжемся с вами.": "Request sent. We will contact you.",
    "Русский": "Russian",
    "O'zbekcha": "Oʻzbekcha",
    "English": "English",
    "Дистрибьютор продуктов питания в Узбекистане": "Food distributor in Uzbekistan",
    "Назад": "Back",
    "Далее": "Next",
    "Хлебные крошки": "Breadcrumbs",
    "Политика приватности": "Privacy policy",
    "Закрыть": "Close",
    "Связаться с нами": "Contact us",
    "Оставьте заявку — мы ответим и подготовим коммерческое предложение.": (
        "Leave a request — we will reply and prepare a commercial offer."
    ),
    "Дистрибьютор продуктов питания в Республике Узбекистан": (
        "Food distributor in the Republic of Uzbekistan"
    ),
    "Дистрибьютор азиатской и специализированной бакалеи для магазинов, HoReCa и партнёров.": (
        "Distributor of Asian and specialty groceries for stores, HoReCa and partners."
    ),
    "Меню": "Menu",
    "Навигация": "Navigation",
    "Все права защищены.": "All rights reserved.",
    "Политика конфиденциальности": "Privacy policy",
    "Основная навигация": "Main navigation",
    "Категории продуктов": "Product categories",
    "Смотреть весь каталог": "View full catalog",
    "Связаться": "Contact",
    "Закрыть меню": "Close menu",
    "Контент скоро появится.": "Content coming soon.",
    "Дистрибьютор продуктов питания": "Food distributor",
    "Каталог AJERES": "AJERES Catalog",
    "Все товары": "All products",
    "Истории партнёров": "Partner stories",
    "Начнём сотрудничество?": "Shall we start working together?",
    "Пришлём актуальный прайс и подберём ассортимент под ваш формат бизнеса.": (
        "We’ll send an up-to-date price list and tailor the assortment to your business."
    ),
    "Свяжитесь с нами в любое удобное время, профессиональная команда специалистов готова ответить на все вопросы и обсудить взаимовыгодное сотрудничество": (
        "Contact us at any convenient time — our professional team is ready to answer "
        "all questions and discuss mutually beneficial cooperation"
    ),
    "Сотрудничество": "Partnership",
    "Для торговых сетей, дистрибьюторов и HoReCa": (
        "For retail chains, distributors and HoReCa"
    ),
    "Компания ООО «AJERES» предлагает широкий ассортимент качественных продуктов питания от международных производителей.": (
        "AJERES LLC offers a wide range of quality food products from international producers."
    ),
    "Нашим партнерам мы гарантируем:": "We guarantee our partners:",
    "Стабильные поставки": "Stable supply",
    "Конкурентные цены": "Competitive prices",
    "Широкий ассортимент": "A broad assortment",
    "Маркетинговую поддержку": "Marketing support",
    "Оперативную логистику": "Responsive logistics",
    "Персональное сопровождение": "Personal account care",
    "Профессиональную работу торговой команды": "A professional sales team",
    "Мы стремимся строить долгосрочные отношения, основанные на доверии, прозрачности и взаимной выгоде.": (
        "We strive to build long-term relationships based on trust, transparency "
        "and mutual benefit."
    ),
    "Производители, которых мы представляем": "Manufacturers we represent",
    "Написать на почту": "Email us",
    "Наш каталог": "Our catalog",
    "Фильтруйте по категориям или ищите по названию. Под каталогом — бренды-производители.": (
        "Filter by category or search by name. Brands are listed below the catalog."
    ),
    "Категории": "Categories",
    "Все": "All",
    "Поиск": "Search",
    "Поиск товаров…": "Search products…",
    "Наши бренды": "Our brands",
    "Производители, которые мы представляем": "Producers we represent",
    "Смотреть товары": "View products",
    "Ничего не найдено": "Nothing found",
    "Сбросить": "Reset",
    "Показано %(start)s–%(end)s из %(total)s": "Showing %(start)s–%(end)s of %(total)s",
    "Страницы": "Pages",
    "С какой целью обращаетесь": "What is the purpose of your request",
    "Имя": "Name",
    "Телефон": "Phone",
    "Электронная почта": "Email",
    "Отправить": "Send",
    "Например: интересует оптовый прайс на соусы и лапшу": (
        "For example: interested in wholesale prices for sauces and noodles"
    ),
    "Ваше имя": "Your name",
    "you@company.com": "you@company.com",
    "Заявка отправлена": "Request sent",
    "Мы свяжемся с вами в ближайшее время.": "We will contact you shortly.",
    "Дистрибьютор с 2018 года": "Distributor since 2018",
    "Мы выводим лучшие бренды на рынок Узбекистана": (
        "We bring the best brands to the Uzbekistan market"
    ),
    "Лучшие бренды в своем сегменте на рынке Узбекистана": (
        "The best brands in their segment on the Uzbekistan market"
    ),
    "Импорт, эксклюзивная дистрибуция, вывод на рынок Узбекистана новых производителей.": (
        "Import, exclusive distribution, and bringing new producers to the Uzbekistan market."
    ),
    "ООО «AJERES» — современная дистрибьюторская компания: импорт, логистика, продажи, маркетинг и развитие брендов.": (
        "AJERES LLC is a modern distribution company: import, logistics, sales, "
        "marketing and brand development."
    ),
    "Наши услуги": "Our services",
    "Наша деятельность": "Our activities",
    "Мы гордимся сотрудничеством с международными производителями, которые доверили нам развитие своих брендов на рынке Узбекистана.": (
        "We are proud to partner with international producers who entrusted us with "
        "developing their brands in Uzbekistan."
    ),
    "Эксклюзивно представляем производителей сильных брендов, которые доверяют нам свое развитие": (
        "We exclusively represent strong brand producers who trust us with their growth"
    ),
    "Производители, которые мы представляем": "Producers we represent",
    "Язык": "Language",
    "Разработано студией": "Developed by",
    "ООО": "LLC",
    "ООО «AJERES»": "AJERES LLC",
    "Свяжитесь": "Contact",
    "с нами": "us",
    "Адрес": "Address",
    "Почта": "Email",
    "Построить маршрут": "Get directions",
    "Фильтр": "Filter",
}

UZ = {
    "Главная": "Bosh sahifa",
    "Продукты": "Mahsulotlar",
    "Каталог": "Katalog",
    "О компании": "Kompaniya haqida",
    "Контакты": "Aloqa",
    "Слишком много заявок. Попробуйте позже.": "So‘rovlar juda ko‘p. Keyinroq urinib ko‘ring.",
    "Заявка отправлена. Мы свяжемся с вами.": "So‘rov yuborildi. Tez orada bog‘lanamiz.",
    "Русский": "Ruscha",
    "O'zbekcha": "Oʻzbekcha",
    "English": "Inglizcha",
    "Дистрибьютор продуктов питания в Узбекистане": "O‘zbekistonda oziq-ovqat distribyutori",
    "Назад": "Orqaga",
    "Далее": "Keyingi",
    "Хлебные крошки": "Navigatsiya izi",
    "Политика приватности": "Maxfiylik siyosati",
    "Закрыть": "Yopish",
    "Связаться с нами": "Biz bilan bog‘laning",
    "Оставьте заявку — мы ответим и подготовим коммерческое предложение.": (
        "So‘rov qoldiring — javob beramiz va tijorat taklifini tayyorlaymiz."
    ),
    "Дистрибьютор продуктов питания в Республике Узбекистан": (
        "O‘zbekiston Respublikasida oziq-ovqat mahsulotlari distribyutori"
    ),
    "Дистрибьютор азиатской и специализированной бакалеи для магазинов, HoReCa и партнёров.": (
        "Do‘konlar, HoReCa va hamkorlar uchun Osiyo va maxsus bakalya distribyutori."
    ),
    "Меню": "Menyu",
    "Навигация": "Navigatsiya",
    "Все права защищены.": "Barcha huquqlar himoyalangan.",
    "Политика конфиденциальности": "Maxfiylik siyosati",
    "Основная навигация": "Asosiy navigatsiya",
    "Категории продуктов": "Mahsulot kategoriyalari",
    "Смотреть весь каталог": "Butun katalogni ko‘rish",
    "Связаться": "Bog‘lanish",
    "Закрыть меню": "Menyuni yopish",
    "Контент скоро появится.": "Kontent tez orada paydo bo‘ladi.",
    "Дистрибьютор продуктов питания": "Oziq-ovqat distribyutori",
    "Каталог AJERES": "AJERES katalogi",
    "Все товары": "Barcha mahsulotlar",
    "Истории партнёров": "Hamkorlar hikoyalari",
    "Начнём сотрудничество?": "Hamkorlikni boshlaymizmi?",
    "Пришлём актуальный прайс и подберём ассортимент под ваш формат бизнеса.": (
        "Aktual narxlar ro‘yxatini yuboramiz va assortimentni biznesingizga moslaymiz."
    ),
    "Свяжитесь с нами в любое удобное время, профессиональная команда специалистов готова ответить на все вопросы и обсудить взаимовыгодное сотрудничество": (
        "Biz bilan qulay vaqtda bog‘laning — professional mutaxassislar jamoasi barcha "
        "savollaringizga javob berishga va o‘zaro manfaatli hamkorlikni muhokama qilishga tayyor"
    ),
    "Сотрудничество": "Hamkorlik",
    "Для торговых сетей, дистрибьюторов и HoReCa": (
        "Savdo tarmoqlari, distribyutorlar va HoReCa uchun"
    ),
    "Компания ООО «AJERES» предлагает широкий ассортимент качественных продуктов питания от международных производителей.": (
        '"AJERES" MChJ xalqaro ishlab chiqaruvchilarning keng assortimentdagi sifatli '
        'oziq-ovqat mahsulotlarini taklif etadi.'
    ),
    "Нашим партнерам мы гарантируем:": "Hamkorlarimizga quyidagilarni kafolatlaymiz:",
    "Стабильные поставки": "Barqaror yetkazib berish",
    "Конкурентные цены": "Raqobatbardosh narxlar",
    "Широкий ассортимент": "Keng assortiment",
    "Маркетинговую поддержку": "Marketing qo‘llab-quvvatlovi",
    "Оперативную логистику": "Tezkor logistika",
    "Персональное сопровождение": "Shaxsiy yondashuv",
    "Профессиональную работу торговой команды": "Professional savdo jamoasi",
    "Мы стремимся строить долгосрочные отношения, основанные на доверии, прозрачности и взаимной выгоде.": (
        "Biz ishonch, ochiqlik va o‘zaro manfaat tamoyillariga asoslangan uzoq muddatli "
        "hamkorlikni yo‘lga qo‘yishga intilamiz."
    ),
    "Производители, которых мы представляем": (
        "Biz vakili bo‘lgan ishlab chiqaruvchilar"
    ),
    "Написать на почту": "Email yozish",
    "Наш каталог": "Bizning katalog",
    "Фильтруйте по категориям или ищите по названию. Под каталогом — бренды-производители.": (
        "Kategoriya bo‘yicha filtrlang yoki nom bo‘yicha qidiring. Katalog ostida — brendlar."
    ),
    "Категории": "Kategoriyalar",
    "Все": "Hammasi",
    "Поиск": "Qidiruv",
    "Поиск товаров…": "Mahsulotlarni qidirish…",
    "Наши бренды": "Bizning brendlar",
    "Производители, которые мы представляем": "Biz vakili bo‘lgan ishlab chiqaruvchilar",
    "Смотреть товары": "Mahsulotlarni ko‘rish",
    "Ничего не найдено": "Hech narsa topilmadi",
    "Сбросить": "Tozalash",
    "Показано %(start)s–%(end)s из %(total)s": "%(total)s dan %(start)s–%(end)s ko‘rsatilmoqda",
    "Страницы": "Sahifalar",
    "С какой целью обращаетесь": "Murojaat maqsadi",
    "Имя": "Ism",
    "Телефон": "Telefon",
    "Электронная почта": "Elektron pochta",
    "Отправить": "Yuborish",
    "Например: интересует оптовый прайс на соусы и лапшу": (
        "Masalan: souslar va lag‘mon uchun ulgurji narxlar qiziqtiradi"
    ),
    "Ваше имя": "Ismingiz",
    "you@company.com": "you@company.com",
    "Заявка отправлена": "So‘rov yuborildi",
    "Мы свяжемся с вами в ближайшее время.": "Tez orada siz bilan bog‘lanamiz.",
    "Дистрибьютор с 2018 года": "2018-yildan beri distribyutor",
    "Мы выводим лучшие бренды на рынок Узбекистана": (
        "Eng yaxshi brendlarni O‘zbekiston bozoriga olib chiqamiz"
    ),
    "Лучшие бренды в своем сегменте на рынке Узбекистана": (
        "O‘zbekiston bozorida o‘z segmentidagi eng yaxshi brendlar"
    ),
    "Импорт, эксклюзивная дистрибуция, вывод на рынок Узбекистана новых производителей.": (
        "Import, eksklyuziv distribyutsiya, yangi ishlab chiqaruvchilarni O‘zbekiston "
        "bozoriga olib chiqish."
    ),
    "ООО «AJERES» — современная дистрибьюторская компания: импорт, логистика, продажи, маркетинг и развитие брендов.": (
        "«AJERES» MChJ — zamonaviy distribyutor kompaniya: import, logistika, savdo, "
        "marketing va brend rivojlantirish."
    ),
    "Наши услуги": "Bizning xizmatlar",
    "Наша деятельность": "Bizning faoliyatimiz",
    "Мы гордимся сотрудничеством с международными производителями, которые доверили нам развитие своих брендов на рынке Узбекистана.": (
        "O‘zbekiston bozorida brendlarini rivojlantirishni ishonib topshirgan xalqaro "
        "ishlab chiqaruvchilar bilan hamkorlikdan faxrlanamiz."
    ),
    "Эксклюзивно представляем производителей сильных брендов, которые доверяют нам свое развитие": (
        "Rivojlanishini bizga ishonib topshirgan kuchli brend ishlab chiqaruvchilarini "
        "eksklyuziv ravishda taqdim etamiz"
    ),
    "Производители, которые мы представляем": "Biz vakili bo‘lgan ishlab chiqaruvchilar",
    "Язык": "Til",
    "Разработано студией": "Ishlab chiqilgan",
    "ООО": "MChJ",
    "ООО «AJERES»": "«AJERES» MChJ",
    "Свяжитесь": "Bog‘laning",
    "с нами": "biz bilan",
    "Адрес": "Manzil",
    "Почта": "Pochta",
    "Построить маршрут": "Marshrut qurish",
    "Фильтр": "Filtr",
}


def _unescape_po(s: str) -> str:
    # Keep UTF-8 text intact; only resolve PO string escapes.
    return (
        s.replace("\\\\", "\0")
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\0", "\\")
    )


def _escape_po(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def fill_po(path: Path, mapping: dict[str, str], lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("#, fuzzy\n", "")
    text = re.sub(
        r'"Language:.*\\n"',
        f'"Language: {lang}\\n"',
        text,
        count=1,
    )

    pattern = re.compile(
        r'(msgid (?:"(?:\\.|[^"\\])*"\s*)+)\s*'
        r'(msgstr (?:"(?:\\.|[^"\\])*"\s*)*)',
        re.MULTILINE,
    )

    def repl(match: re.Match) -> str:
        msgid_block = match.group(1)
        parts = re.findall(r'"((?:\\.|[^"\\])*)"', msgid_block)
        msgid = _unescape_po("".join(parts))
        if msgid == "":
            return match.group(0)
        translation = mapping.get(msgid)
        if translation is None:
            return match.group(0)
        return f'{msgid_block}msgstr "{_escape_po(translation)}"\n'

    new_text, n = pattern.subn(repl, text)
    path.write_text(new_text, encoding="utf-8")
    print(f"{path}: filled {n} entries")


def main() -> None:
    fill_po(ROOT / "locale/en/LC_MESSAGES/django.po", EN, "en")
    fill_po(ROOT / "locale/uz/LC_MESSAGES/django.po", UZ, "uz")


if __name__ == "__main__":
    main()
