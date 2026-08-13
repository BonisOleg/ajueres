"""CMS SiteBlock translations (ru/uz/en) for seed — fill empty lang fields only."""

from __future__ import annotations

# (page, key) → {ru, uz, en}
BLOCK_I18N: dict[tuple[str, str], dict[str, str]] = {
    ('home', 'hero_eyebrow'): {
        'ru': 'Дистрибьютор с 2018 года',
        'uz': '2018-yildan beri distribyutor',
        'en': 'Distributor since 2018',
    },
    ('home', 'hero_title'): {
        'ru': 'Лучшие бренды в своем сегменте на рынке Узбекистана',
        'uz': 'O‘zbekiston bozorida o‘z segmentidagi eng yaxshi brendlar',
        'en': 'The best brands in their segment on the Uzbekistan market',
    },
    ('home', 'hero_text'): {
        'ru': (
            'Импорт, эксклюзивная дистрибуция, вывод на рынок Узбекистана '
            'новых производителей.'
        ),
        'uz': (
            'Import, eksklyuziv distribyutsiya, yangi ishlab chiqaruvchilarni '
            'O‘zbekiston bozoriga olib chiqish.'
        ),
        'en': (
            'Import, exclusive distribution, and bringing new producers '
            'to the Uzbekistan market.'
        ),
    },
    ('home', 'hero_cta'): {
        'ru': 'Связаться с нами',
        'uz': 'Biz bilan bog‘laning',
        'en': 'Contact us',
    },
    ('home', 'services_title'): {
        'ru': 'Наша деятельность',
        'uz': 'Bizning faoliyatimiz',
        'en': 'Our activities',
    },
    ('home', 'brands_title'): {
        'ru': 'Наши партнёры',
        'uz': 'Bizning hamkorlarimiz',
        'en': 'Our partners',
    },
    ('home', 'brands_subtitle'): {
        'ru': (
            'Ритейл-партнёры и производители, с которыми мы развиваем '
            'ассортимент на рынке Узбекистана'
        ),
        'uz': (
            'Biz O‘zbekiston bozorida assortimentni birga rivojlantirayotgan '
            'chakana savdo hamkorlari va ishlab chiqaruvchilar'
        ),
        'en': (
            'Retail partners and manufacturers with whom we grow the '
            'assortment in Uzbekistan'
        ),
    },
    ('home', 'coop_title'): {
        'ru': 'Сотрудничество',
        'uz': 'Hamkorlik',
        'en': 'Partnership',
    },
    ('home', 'coop_eyebrow'): {
        'ru': 'Для торговых сетей, дистрибьюторов и HoReCa',
        'uz': 'Savdo tarmoqlari, distribyutorlar va HoReCa uchun',
        'en': 'For retail chains, distributors and HoReCa',
    },
    ('home', 'coop_cta'): {
        'ru': 'Стать партнером',
        'uz': 'Hamkor bo‘lish',
        'en': 'Become a partner',
    },
    ('home', 'cta_title'): {
        'ru': 'Начнём сотрудничество?',
        'uz': 'Hamkorlikni boshlaymizmi?',
        'en': 'Shall we start working together?',
    },
    ('home', 'cta_text'): {
        'ru': (
            'Свяжитесь с нами в любое удобное время, профессиональная команда '
            'специалистов готова ответить на все вопросы и обсудить '
            'взаимовыгодное сотрудничество'
        ),
        'uz': (
            'Biz bilan istalgan qulay vaqtda bog‘laning — professional jamoa '
            'barcha savollaringizga javob berishga va o‘zaro manfaatli '
            'hamkorlikni muhokama qilishga tayyor'
        ),
        'en': (
            'Contact us at any convenient time — our professional team is '
            'ready to answer all questions and discuss mutually beneficial '
            'cooperation'
        ),
    },
    ('about', 'eyebrow'): {
        'ru': 'О компании',
        'uz': 'Kompaniya haqida',
        'en': 'About',
    },
    ('about', 'title'): {
        'ru': 'ООО «AJERES»',
        'uz': '«AJERES» MChJ',
        'en': 'AJERES LLC',
    },
    ('about', 'intro'): {
        'ru': (
            'Современная дистрибьюторская компания на рынке продуктов '
            'питания Республики Узбекистан. Специализируемся на выводе '
            'международных брендов и полном комплексе услуг: импорт, '
            'логистика, продажи, маркетинг и развитие брендов.'
        ),
        'uz': (
            'O‘zbekiston Respublikasi oziq-ovqat bozoridagi zamonaviy '
            'distribyutorlik kompaniyasi. Xalqaro brendlarni bozorga chiqarish '
            'hamda to‘liq xizmatlar majmuasi: import, logistika, savdo, '
            'marketing va brendlarni rivojlantirish.'
        ),
        'en': (
            'A modern food distribution company in Uzbekistan. We specialize '
            'in launching international brands and a full service cycle: '
            'import, logistics, sales, marketing and brand development.'
        ),
    },
    ('about', 'cta'): {
        'ru': 'Связаться с нами',
        'uz': 'Biz bilan bog‘laning',
        'en': 'Contact us',
    },
    ('contacts', 'eyebrow'): {
        'ru': 'Контакты',
        'uz': 'Aloqa',
        'en': 'Contacts',
    },
    ('contacts', 'title'): {
        'ru': 'Свяжитесь с нами',
        'uz': 'Biz bilan bog‘laning',
        'en': 'Contact us',
    },
    ('site', 'nav_home'): {
        'ru': 'Главная',
        'uz': 'Bosh sahifa',
        'en': 'Home',
    },
    ('site', 'nav_catalog'): {
        'ru': 'Каталог',
        'uz': 'Katalog',
        'en': 'Catalog',
    },
    ('site', 'nav_about'): {
        'ru': 'О компании',
        'uz': 'Kompaniya haqida',
        'en': 'About',
    },
    ('site', 'nav_contacts'): {
        'ru': 'Контакты',
        'uz': 'Aloqa',
        'en': 'Contacts',
    },
    ('site', 'nav_mega_label'): {
        'ru': 'Категории продуктов',
        'uz': 'Mahsulot kategoriyalari',
        'en': 'Product categories',
    },
    ('site', 'nav_mega_all'): {
        'ru': 'Смотреть весь каталог',
        'uz': 'Butun katalogni ko‘rish',
        'en': 'View full catalog',
    },
    ('site', 'cta'): {
        'ru': 'Связаться',
        'uz': 'Bog‘lanish',
        'en': 'Contact',
    },
    ('site', 'cta_mobile'): {
        'ru': 'Связаться с нами',
        'uz': 'Biz bilan bog‘laning',
        'en': 'Contact us',
    },
    ('site', 'tagline'): {
        'ru': 'Дистрибьютор продуктов питания в Республике Узбекистан',
        'uz': 'O‘zbekiston Respublikasida oziq-ovqat mahsulotlari distribyutori',
        'en': 'Food distributor in the Republic of Uzbekistan',
    },
    ('site', 'credit'): {
        'ru': 'Разработано студией',
        'uz': 'Studiya tomonidan ishlab chiqilgan',
        'en': 'Designed by',
    },
    ('site', 'copyright'): {
        'ru': 'Все права защищены.',
        'uz': 'Barcha huquqlar himoyalangan.',
        'en': 'All rights reserved.',
    },
    ('site', 'menu_label'): {
        'ru': 'Меню',
        'uz': 'Menyu',
        'en': 'Menu',
    },
    ('site', 'contacts_label'): {
        'ru': 'Контакты',
        'uz': 'Aloqa',
        'en': 'Contacts',
    },
}
