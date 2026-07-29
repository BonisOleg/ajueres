#!/usr/bin/env python3
"""Fill locale/*/LC_MESSAGES/django.po msgstr from translation maps."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EN = {
    "Главная": "Home",
    "Продукты": "Products",
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
    "Заявка отправлена": "Request sent",
    "Мы свяжемся с вами в ближайшее время.": "We will contact you shortly.",
    "Дистрибьютор с 2018 года": "Distributor since 2018",
    "Мы выводим лучшие бренды на рынок Узбекистана": (
        "We bring the best brands to the Uzbekistan market"
    ),
    "ООО «AJERES» — современная дистрибьюторская компания: импорт, логистика, продажи, маркетинг и развитие брендов.": (
        "AJERES LLC is a modern distribution company: import, logistics, sales, "
        "marketing and brand development."
    ),
    "Наши услуги": "Our services",
    "Мы гордимся сотрудничеством с международными производителями, которые доверили нам развитие своих брендов на рынке Узбекистана.": (
        "We are proud to partner with international producers who entrusted us with "
        "developing their brands in Uzbekistan."
    ),
    "Язык": "Language",
}

UZ = {
    "Главная": "Bosh sahifa",
    "Продукты": "Mahsulotlar",
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
    "Заявка отправлена": "So‘rov yuborildi",
    "Мы свяжемся с вами в ближайшее время.": "Tez orada siz bilan bog‘lanamiz.",
    "Дистрибьютор с 2018 года": "2018-yildan beri distribyutor",
    "Мы выводим лучшие бренды на рынок Узбекистана": (
        "Eng yaxshi brendlarni O‘zbekiston bozoriga olib chiqamiz"
    ),
    "ООО «AJERES» — современная дистрибьюторская компания: импорт, логистика, продажи, маркетинг и развитие брендов.": (
        "«AJERES» MChJ — zamonaviy distribyutor kompaniya: import, logistika, savdo, "
        "marketing va brend rivojlantirish."
    ),
    "Наши услуги": "Bizning xizmatlar",
    "Мы гордимся сотрудничеством с международными производителями, которые доверили нам развитие своих брендов на рынке Узбекистана.": (
        "O‘zbekiston bozorida brendlarini rivojlantirishni ishonib topshirgan xalqaro "
        "ishlab chiqaruvchilar bilan hamkorlikdan faxrlanamiz."
    ),
    "Язык": "Til",
}


def _unescape_po(s: str) -> str:
    return bytes(s, "utf-8").decode("unicode_escape")


def _escape_po(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def fill_po(path: Path, mapping: dict[str, str], lang: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("#, fuzzy\n", "")
    text = re.sub(r"Language:.*\n", f"Language: {lang}\n", text, count=1)

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
