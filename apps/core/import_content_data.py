"""Static CMS/catalog content for import_live_content management command."""

from pathlib import Path

NAME_FIX_BY_IMG = {}

# (slug, name_ru, name_uz, name_en, order, parent_slug|None)
CATEGORIES = [
    ('sauces', 'Соусы', 'Souslar', 'Sauces', 0, None),
    ('noodles', 'Лапша', 'Lag‘mon', 'Noodles', 1, None),
    (
        'seaweed',
        'Продукты из морских водорослей',
        'Dengiz suv o‘tlari mahsulotlari',
        'Seaweed products',
        2,
        None,
    ),
    (
        'rice-paper',
        'Рисовая бумага',
        'Guruch qog‘ozi',
        'Rice paper',
        3,
        None,
    ),
    ('snacks', 'Снеки', 'Sneklar', 'Snacks', 4, None),
    ('chips', 'Чипсы', 'Chipslar', 'Chips', 0, 'snacks'),
    ('bruschetta', 'Брускетта', 'Brusketta', 'Bruschetta', 1, 'snacks'),
    ('crush', 'Краш', 'Krash', 'Crush', 2, 'snacks'),
]

INACTIVE_CATEGORY_SLUGS = ('syrups',)

HOME_BLOCKS = {
    'hero_visible': '1',
    'advantages_visible': '1',
    'brands_visible': '1',
    'cases_visible': '0',
    'hero_eyebrow': 'Дистрибьютор с 2018 года',
    'hero_title': 'Лучшие бренды в своем сегменте на рынке Узбекистана',
    'hero_text': (
        'Импорт, эксклюзивная дистрибуция, вывод на рынок Узбекистана '
        'новых производителей.'
    ),
    'hero_cta': 'Связаться с нами',
    'services_title': 'Наша деятельность',
    'brands_title': 'Наши партнёры',
    'brands_subtitle': (
        'Ритейл-партнёры и производители, с которыми мы развиваем '
        'ассортимент на рынке Узбекистана'
    ),
}

ABOUT_BLOCKS = {
    'eyebrow': 'О компании',
    'title': 'ООО «AJERES»',
    'intro': (
        'Современная дистрибьюторская компания на рынке продуктов питания '
        'Республики Узбекистан. Специализируемся на выводе международных '
        'брендов и полном комплексе услуг: импорт, логистика, продажи, '
        'маркетинг и развитие брендов.'
    ),
    'cta': 'Связаться с нами',
}

CONTACTS_INTRO = (
    'Команда ООО «AJERES» всегда открыта для новых партнерств и готова '
    'обсудить возможности сотрудничества.\n\n'
    'Если вы являетесь производителем продуктов питания, представителем '
    'торговой сети или заинтересованы в развитии вашего бренда на рынке '
    'Узбекистана, свяжитесь с нами.\n\n'
    'Мы ответим на все вопросы, подготовим коммерческое предложение и '
    'предложим оптимальную стратегию выхода на рынок.'
)

CONTACTS_BLOCKS = {
    'eyebrow': 'Контакты',
    'title': 'Свяжитесь с нами',
    'intro': CONTACTS_INTRO,
    'partners_title': 'Сотрудничество',
    'form_title': 'Форма заявки',
    'form_lead': CONTACTS_INTRO,
    'map_title': 'Наш офис в Ташкенте',
}

ADVANTAGE_ROWS = [
    (
        'logistics',
        'Импорт продукции',
        (
            'Сопровождение международных поставок. Организуем полный цикл '
            'поставок продуктов питания со всего мира. Весь спектр '
            'логистических услуг, собственный транспорт и складские площади.'
        ),
        'Mahsulotlarni import qilish',
        (
            'Xalqaro yetkazib berish jarayonlarini to‘liq tashkil etamiz. '
            'Dunyoning turli mamlakatlaridan oziq-ovqat mahsulotlarini '
            'yetkazib berishning barcha bosqichlarini boshqaramiz. Logistika '
            'xizmatlarining to‘liq spektri, o‘z transportimiz va omborxonalarimiz.'
        ),
        'Product import',
        (
            'Full-cycle international food supply from around the world: '
            'logistics, own transport and warehousing.'
        ),
    ),
    (
        'brands',
        'Эксклюзивная дистрибуция',
        (
            'Представляем интересы производителя на территории Узбекистана '
            'и отвечаем за развитие бренда. Мы заинтересованы в долгосрочном '
            'успехе наших брендов.'
        ),
        'Eksklyuziv distribyutsiya',
        (
            'Ishlab chiqaruvchining O‘zbekiston hududidagi manfaatlarini '
            'himoya qilamiz va brendni rivojlantirish uchun javob beramiz. '
            'Biz uchun brendlarning uzoq muddatli muvaffaqiyati muhim.'
        ),
        'Exclusive distribution',
        (
            'We represent producers in Uzbekistan and are responsible for '
            'brand development and long-term success.'
        ),
    ),
    (
        'terms',
        'Работа с торговыми сетями',
        (
            'Обеспечиваем листинг продукции, ведём переговоры, сопровождаем '
            'коммерческие условия и развиваем сотрудничество с крупнейшими '
            'розничными сетями.'
        ),
        'Savdo tarmoqlari bilan ishlash',
        (
            'Mahsulotlarni savdo tarmoqlariga kiritishni (listing), muzokaralarni '
            'olib borishni, tijorat shartlarini yuritishni hamda yirik chakana '
            'savdo tarmoqlari bilan hamkorlikni rivojlantirishni ta’minlaymiz.'
        ),
        'Retail network development',
        (
            'Listing, negotiations, commercial terms and partnerships with '
            'major retail chains.'
        ),
    ),
    (
        'assortment',
        'Продажи',
        (
            'Развиваем продажи через торговые сети, традиционную розницу, '
            'оптовые компании, HoReCa, онлайн-розницу и корпоративных клиентов.'
        ),
        'Savdo',
        (
            'Savdoni chakana savdo tarmoqlari, an’anaviy chakana savdo, '
            'ulgurji kompaniyalar, HoReCa, onlayn savdo va korporativ '
            'mijozlar orqali rivojlantiramiz.'
        ),
        'Sales',
        (
            'We grow sales through retail chains, traditional trade, '
            'wholesale, HoReCa, e-commerce and corporate clients.'
        ),
    ),
    (
        'experience',
        'Маркетинг',
        (
            'Разрабатываем и реализуем программы продвижения для роста '
            'узнаваемости бренда и увеличения продаж: рекламные кампании, '
            'дегустации, промо-акции, трейд-маркетинг, оформление торговых '
            'точек и цифровой маркетинг.'
        ),
        'Marketing',
        (
            'Brendning tan olinishi va savdo hajmini oshirishga qaratilgan '
            'marketing dasturlarini ishlab chiqamiz: reklama kampaniyalari, '
            'degustatsiyalar, promo-aksiyalar, treyd-marketing, savdo '
            'nuqtalarini bezatish va raqamli marketing.'
        ),
        'Marketing',
        (
            'Brand promotion programs: campaigns, tastings, promos, '
            'trade marketing, in-store branding and digital marketing.'
        ),
    ),
    (
        'analytics',
        'Аналитика',
        (
            'Предоставляем регулярную отчётность по продажам, остаткам, '
            'развитию дистрибуции и эффективности маркетинговых мероприятий.'
        ),
        'Tahlil',
        (
            'Savdo natijalari, ombor qoldiqlari, distribyutsiya rivoji va '
            'marketing faoliyati samaradorligi bo‘yicha muntazam hisobotlarni '
            'taqdim etamiz.'
        ),
        'Analytics',
        (
            'Regular reporting on sales, stock, distribution growth and '
            'marketing performance.'
        ),
    ),
]

STAT_ROWS = [
    ('2000+', 'магазинов', 'do‘konlar', 'stores'),
    ('80+', 'видов товаров', 'mahsulot turlari', 'product types'),
    ('8+', 'лет на рынке', 'yillik tajriba', 'years on the market'),
    ('39M+', 'население рынка', 'bozor aholisi', 'market population'),
]

ABOUT_SECTIONS = [
    (
        'about',
        'О компании',
        'Kompaniya haqida',
        'About the company',
        (
            'ООО «AJERES» — современная дистрибьюторская компания, работающая '
            'на рынке продуктов питания Республики Узбекистан.\n\n'
            'Мы специализируемся на выводе международных брендов на местный рынок '
            'и обеспечиваем полный комплекс услуг: импорт, логистику, продажи, '
            'маркетинг и развитие брендов.'
        ),
        (
            '"AJERES" MChJ — O‘zbekiston Respublikasi oziq-ovqat mahsulotlari '
            'bozorida faoliyat yurituvchi zamonaviy distribyutorlik kompaniyasi.\n\n'
            'Biz xalqaro brendlarni mahalliy bozorga olib kirishga ixtisoslashganmiz '
            'hamda import, logistika, savdo, marketing va brendlarni rivojlantirish '
            'bo‘yicha to‘liq xizmatlar majmuasini taqdim etamiz.'
        ),
        (
            'AJERES LLC is a modern food distribution company operating in the '
            'Republic of Uzbekistan.\n\n'
            'We specialize in bringing international brands to the local market and '
            'provide a full cycle of services: import, logistics, sales, marketing '
            'and brand development.'
        ),
    ),
    (
        'philosophy',
        'Философия и партнёры',
        'Falsafa va hamkorlar',
        'Philosophy and partners',
        (
            'Наша философия основана на долгосрочном сотрудничестве. Мы рассматриваем '
            'каждого производителя как стратегического партнера и инвестируем свои '
            'знания, ресурсы и опыт в развитие его бренда.\n\n'
            'Компания ООО «AJERES» сотрудничает с ведущими международными '
            'производителями, помогая им успешно выйти на рынок, занять свою нишу '
            'и обеспечить стабильный рост продаж.'
        ),
        (
            'Bizning falsafamiz uzoq muddatli hamkorlikka asoslangan. Har bir '
            'ishlab chiqaruvchini strategik hamkor sifatida ko‘ramiz va uning '
            'brendini rivojlantirish uchun o‘z bilimimiz, tajribamiz va '
            'resurslarimizni safarbar etamiz.\n\n'
            '"AJERES" MChJ yetakchi xalqaro ishlab chiqaruvchilar bilan hamkorlik '
            'qilib, ularga O‘zbekiston bozoriga muvaffaqiyatli kirish, o‘z o‘rnini '
            'egallash va barqaror savdo o‘sishiga erishishda yordam beradi.'
        ),
        (
            'Our philosophy is built on long-term partnership. We treat every '
            'producer as a strategic partner and invest our knowledge, resources '
            'and experience in growing their brand.\n\n'
            'AJERES LLC works with leading international producers, helping them '
            'enter the market, secure their niche and achieve stable sales growth.'
        ),
    ),
    (
        'analytics',
        'Аналитика и сопровождение',
        'Tahlil va qo‘llab-quvvatlash',
        'Analytics and support',
        (
            'Благодаря внимательному анализу рынка, поведения покупателей и '
            'конкурентной среды наша команда профессионалов предложит наиболее '
            'эффективную стратегию продвижения.\n\n'
            'Глубокое знание рынка, развитая сеть продаж и комплексный подход, '
            'сопровождение бренда на каждом этапе — от первых поставок до '
            'масштабного присутствия в крупнейших торговых сетях страны.'
        ),
        (
            'Bozor, iste’molchilar xulq-atvori va raqobat muhitini chuqur tahlil '
            'qilish orqali mutaxassislarimiz brendingizni rivojlantirish uchun eng '
            'samarali strategiyani taklif etadi.\n\n'
            'Bozorni chuqur bilishimiz, rivojlangan savdo tarmog‘imiz va kompleks '
            'yondashuvimiz tufayli biz brendni dastlabki yetkazib berishdan boshlab '
            'mamlakatning yirik savdo tarmoqlarida keng miqyosda namoyon '
            'bo‘lishigacha bo‘lgan barcha bosqichlarda qo‘llab-quvvatlaymiz.'
        ),
        (
            'Through careful analysis of the market, shopper behaviour and the '
            'competitive landscape, our specialists propose the most effective '
            'promotion strategy.\n\n'
            'Deep market knowledge, a developed sales network and an end-to-end '
            'approach accompany the brand at every stage — from the first shipments '
            'to a strong presence in the country’s largest retail chains.'
        ),
    ),
    (
        'responsibility',
        'Ответственность',
        'Mas’uliyat',
        'Responsibility',
        (
            'Успех производителя напрямую зависит от профессионализма и качества '
            'локального партнера.\n\n'
            'Именно поэтому мы берем на себя ответственность '
            'не только за продажи, но и за построение сильной позиции бренда на рынке.'
        ),
        (
            'Ishlab chiqaruvchining muvaffaqiyati ko‘p jihatdan mahalliy hamkorning '
            'professionalligi va ishonchliligiga bog‘liq.\n\n'
            'Shu sababli biz nafaqat '
            'savdo natijalari, balki brendning bozordagi kuchli mavqeini '
            'shakllantirish uchun ham mas’uliyatni o‘z zimmamizga olamiz.'
        ),
        (
            'A producer’s success depends directly on the professionalism and quality '
            'of the local partner.\n\n'
            'That is why we take responsibility not only for '
            'sales, but also for building a strong brand position in the market.'
        ),
    ),
    (
        'market',
        'Потенциал рынка Узбекистана',
        'O‘zbekiston bozori salohiyati',
        'Uzbekistan market potential',
        (
            'Узбекистан является одной из самых быстрорастущих экономик Центральной Азии.\n\n'
            'Основные преимущества рынка:\n'
            '• население более 39 миллионов человек;\n'
            '• молодая и активно растущая аудитория;\n'
            '• ежегодный рост современного ритейла;\n'
            '• высокий спрос на импортные продукты питания;\n'
            '• благоприятный инвестиционный климат;\n'
            '• стратегическое расположение между странами Центральной Азии.\n\n'
            'Эти факторы делают рынок Узбекистана привлекательной площадкой для '
            'международных производителей продуктов питания. Наша компания помогает '
            'партнерам безопасно и эффективно выйти на этот рынок, без риска и '
            'репутационных потерь.'
        ),
        (
            'O‘zbekiston Markaziy Osiyodagi eng tez rivojlanayotgan iqtisodiyotlardan biridir.\n\n'
            'Bozorning asosiy afzalliklari:\n'
            '• 39 milliondan ortiq aholi;\n'
            '• yosh va tez o‘sib borayotgan iste’molchilar auditoriyasi;\n'
            '• zamonaviy chakana savdo tarmoqlarining yillik o‘sishi;\n'
            '• import oziq-ovqat mahsulotlariga yuqori talab;\n'
            '• qulay investitsiya muhiti;\n'
            '• Markaziy Osiyo mamlakatlari o‘rtasidagi strategik geografik joylashuv.\n\n'
            'Mazkur omillar O‘zbekistonni xalqaro oziq-ovqat ishlab chiqaruvchilari '
            'uchun jozibador bozorga aylantiradi. Kompaniyamiz hamkorlarimizga ushbu '
            'bozorga xavfsiz, samarali va reputatsion xatarlarsiz kirishga yordam beradi.'
        ),
        (
            'Uzbekistan is one of the fastest-growing economies in Central Asia.\n\n'
            'Key market advantages:\n'
            '• population of more than 39 million people;\n'
            '• a young and actively growing audience;\n'
            '• annual growth of modern retail;\n'
            '• high demand for imported food products;\n'
            '• a favourable investment climate;\n'
            '• a strategic location between Central Asian countries.\n\n'
            'These factors make Uzbekistan an attractive platform for international '
            'food producers. Our company helps partners enter this market safely and '
            'effectively, without risk or reputational losses.'
        ),
    ),
    (
        'mission',
        'Наша миссия',
        'Bizning missiyamiz',
        'Our mission',
        (
            'Предоставлять потребителям Узбекистана качественные продукты питания '
            'мирового уровня и помогать международным производителям успешно развивать '
            'свой бизнес в Центральной Азии.'
        ),
        (
            'O‘zbekiston iste’molchilariga jahon darajasidagi sifatli oziq-ovqat '
            'mahsulotlarini taqdim etish hamda xalqaro ishlab chiqaruvchilarga '
            'Markaziy Osiyoda o‘z biznesini muvaffaqiyatli rivojlantirishda ko‘maklashish.'
        ),
        (
            'Provide Uzbekistan consumers with world-class food products and help '
            'international producers successfully grow their business in Central Asia.'
        ),
    ),
    (
        'goals',
        'Наши цели',
        'Bizning maqsadlarimiz',
        'Our goals',
        (
            'Стать одним из ведущих дистрибьюторов международных брендов продуктов '
            'питания в регионе.\n\n'
            'Мы выводим мировые бренды на рынок Республики Узбекистан.'
        ),
        (
            'Markaziy Osiyoda xalqaro oziq-ovqat brendlarining yetakchi '
            'distribyutorlaridan biriga aylanish.\n\n'
            'Biz jahon brendlarini O‘zbekiston Respublikasi bozoriga olib chiqamiz.'
        ),
        (
            'Become one of the leading distributors of international food brands '
            'in the region.\n\n'
            'We bring world brands to the market of the Republic of Uzbekistan.'
        ),
    ),
]

PARTNER_ROWS = [
    (
        'Стратегия продвижения',
        'Brendni ilgari surish strategiyasi',
        'Promotion strategy',
        'Помогаем выстроить эффективную стратегию вывода и роста бренда.',
        'Brendni bozorga chiqarish va o‘stirish uchun samarali strategiyani quramiz.',
        'We help build an effective strategy to launch and grow the brand.',
    ),
    (
        'Логистика',
        'Logistika',
        'Logistics',
        'Организация поставок, склад и доставка по сети партнёров.',
        'Yetkazib berish, ombor va hamkorlar tarmog‘i bo‘ylab yetkazib berishni tashkil qilamiz.',
        'Supply organization, warehousing and delivery across the partner network.',
    ),
    (
        'Маркетинговая поддержка',
        'Marketing qo‘llab-quvvatlash',
        'Marketing support',
        'Промо, трейд-маркетинг и digital-инструменты для роста продаж.',
        'Savdo o‘sishi uchun promo, treyd-marketing va digital vositalar.',
        'Promo, trade marketing and digital tools to grow sales.',
    ),
    (
        'Консультации по продажам',
        'Savdo bo‘yicha konsultatsiyalar',
        'Sales consulting',
        'Работа с сетями, HoReCa и традиционной розницей.',
        'Savdo tarmoqlari, HoReCa va an’anaviy chakana savdo bilan ishlash.',
        'Working with retail chains, HoReCa and traditional trade.',
    ),
]

# slug -> (name_ru, name_uz, name_en)
BRAND_I18N = {
    'sen-soy': ('Sen Soy', 'Sen Soy', 'Sen Soy'),
    'paprichi': ('Папричи', 'Paprichi', 'Paprichi'),
    'riceup': ('RICEUP', 'RICEUP', 'RICEUP'),
    'gaudo': ('GAUDO', 'GAUDO', 'GAUDO'),
    'krambals': ('KRAMBALS', 'KRAMBALS', 'KRAMBALS'),
    'yamchan': ('ЯМЧАН', 'Yamchan', 'Yamchan'),
    'huligan': ('HULIGAN', 'HULIGAN', 'HULIGAN'),
    'prince-of-chester': (
        'Prince of Chester',
        'Prince of Chester',
        'Prince of Chester',
    ),
}

from apps.core.legal_defaults import OFFER_DEFAULTS, PRIVACY_DEFAULTS  # noqa: F401

# Local files live in <project>/content/logos/ (supplier pack).
BRAND_LOGOS_DIR = Path(__file__).resolve().parents[2] / 'content' / 'logos'
RETAIL_LOGOS_DIR = BRAND_LOGOS_DIR / 'buyers'
PRODUCT_IMAGES_DIR = Path(__file__).resolve().parents[2] / 'content' / 'products'

BRANDS_SPEC = [
    ('sen-soy', 'Sen Soy', 'sensoy.jpg', 0, True),
    ('paprichi', 'Папричи', 'paprichi.jpg', 1, True),
    ('riceup', 'RICEUP', 'riceup.png', 2, True),
    ('gaudo', 'GAUDO', 'gaudo.jpeg', 3, True),
    ('krambals', 'KRAMBALS', 'krambals.jpg', 4, True),
    ('yamchan', 'ЯМЧАН', 'yamchan.png', 5, True),
    ('huligan', 'HULIGAN', 'huligan.png', 6, True),
    # Legacy brand; tea products removed from catalog.
    ('prince-of-chester', 'Prince of Chester', None, 7, False),
]

# Homepage «Наши бренды» = retail buyers. images.png skipped (unknown name).
RETAIL_PARTNERS_SPEC = [
    ('uzum', 'Uzum', 'uzum.png', 0),
    ('korzinka', 'korzinka.uz', 'korzinka.png', 1),
    ('magnum', 'Magnum', 'magnum.png', 2),
    ('assorti-market', 'Assorti Market', 'assorti-market.png', 3),
    ('olma', 'Olma', 'olma.png', 4),
    ('makro', 'Makro', 'makro.png', 5),
    ('havas', 'HAVAS', 'havas.jpg', 6),
    ('galmart', 'Galmart', 'galmart.png', 7),
    ('carrefour', 'Carrefour', 'carrefour.png', 8),
]

STATIC_BRAND_LOGOS_DIR = Path(__file__).resolve().parents[2] / 'static' / 'img' / 'brands'
STATIC_RETAIL_LOGOS_DIR = Path(__file__).resolve().parents[2] / 'static' / 'img' / 'partners'

BRAND_LOGO_STATIC = {
    slug: f'img/brands/{logo_file}'
    for slug, _name, logo_file, _order, _featured in BRANDS_SPEC
    if logo_file
}
RETAIL_LOGO_STATIC = {
    slug: f'img/partners/{logo_file}'
    for slug, _name, logo_file, _order in RETAIL_PARTNERS_SPEC
    if logo_file
}
