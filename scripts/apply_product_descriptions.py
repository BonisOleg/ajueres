#!/usr/bin/env python3
"""Parse Карточки_товаров.docx and write description_ru/en/uz into catalog JSON."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CATALOG_JSON = ROOT / 'content' / 'catalog_products.json'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

STARTS = [
    r'^Пшеничная лапша Somen',
    r'^Соус «Сладкий ЧИЛИ»',
    r'^Острый чили соус Sriracha',
    r'^Нори — это особый',
    r'^Чипсы «Нори»',
    r'^Соус « ?Жгучий ЧИЛИ»',
    r'^Соевый соус изготовлен методом естественного брожения\. Этот соус, без преувеличения',
    r'^Соевый соус Тёмный',
    r'^Соус Чили Манго',
    r'^Соус «Терияки Сладкий»',
    r'^Соус Унаги',
    r'^Соевый соус изготовлен методом естественного брожения\. Этот соус, без преувеличения',
    r'^Крупная, толстая и плоская лапша Udon',
    r'^Японская яичная лапша',
    r'^Рисовая лапша, названная по-европейски',
    r'^Рисовая лапша в изящной упаковке',
    r'^Суп Том ям',
    r'^Рисовая бумага',
    r'^Чипсы «Нори»',
    r'^Чипсы «Нори»',
    r'^Чипсы «Нори»',
    r'^Чипсы «Нори»',
    r'^Чипсы «Нори»',
    r'^Устричный соус',
    r'^В соусе Чили Свит',
    r'^Кисло-сладкий ананас',
    r'^Белый рисовый уксус',
    r'^Этот соус имеет яркий',
    r'^Лёгкий соевый соус',
    r'^Соус «Вок»',
    r'^Соус жгучий чили - это традиционный',
    r'^Соус Ямчан Чили сладкий',
    r'^Соус соевый ЯМЧАН',
    r'^С соевым соусом терияки',
    r'^Прекрасно подходит для мяса',
    r'^Соевый соус «Суши и сашими»',
    r'^Японский соус «Терияки с кунжутом»',
    r'^Эта лапша принесет подлинный вкус Вьетнама',
    r'^Корейский суп-лапша Рамен',
    r'^Соус «Кисло-сладкий»',
    r'^Соус «Для Барбекю»',
    r'^Соус «Шашлычный»',
    r'^Соус «Остро-сладкий»',
    r'^Каждый хрустящий кусочек наполнен',
    r'^Каждая чипсина',
    r'^Острый вкус: чипсы из коричневого риса',
    r'^Чипсы из коричневого риса со вкусом кетчупа',
    r'^Рисовые чипсы с морской солью',
    r'^Чипсы из коричневого риса со сметаной',
    r'^Насладитесь средиземноморским',
    r'^Попробуйте наши острые чипсы со вкусом сыра начо',
    r'^Хрустите нашими полезными солеными',
    r'^Погрузитесь в сливочно-пикантный мир',
    r'^Насладитесь ярким, дымным вкусом наших чипсов из тортильи',
    r'^Побалуйте себя восхитительным сырным вкусом',
    r'^Хрустящие, золотистые ломтики настоящего хлеба чиабатта\. Созревшие',
    r'^Хрустящие золотистые ломтики настоящего хлеба чиабатта\. Яркие зеленые',
    r'^Хрустящие, золотистые ломтики настоящего хлеба чиабатта\. Ароматные',
    r'^Хрустящие, золотистые ломтики настоящего хлеба чиабатта\. Овощи',
    r'^Хрустящие, золотистые ломтики настоящего хлеба чиабатта\. Землистый',
    r'^Откройте для себя снеки Huligan — хрустящие кусочки кренделя\.Сырный',
    r'^Откройте для себя снеки Huligan — хрустящие кусочки кренделя\.Мед',
    r'^Откройте для себя закуски Huligan — хрустящие кусочки кренделя\. Известный',
    r'^Откройте для себя закуски Huligan — хрустящие кусочки кренделя\.Невероятно',
]


def docx_paragraphs(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read('word/document.xml')
    root = ET.fromstring(xml)
    paras: list[str] = []
    for p in root.findall('.//w:p', NS):
        line = ''.join(t.text or '' for t in p.findall('.//w:t', NS)).strip()
        if line:
            paras.append(line)
    return paras


def chunks_from_paras(paras: list[str]) -> list[str]:
    out: list[str] = []
    pi = 0
    for si, pat in enumerate(STARTS):
        found = None
        for j in range(pi, len(paras)):
            if re.search(pat, paras[j]):
                found = j
                break
        if found is None:
            raise SystemExit(f'Missing start {si}: {pat}')
        nxt = None
        if si + 1 < len(STARTS):
            npat = STARTS[si + 1]
            for j in range(found + 1, len(paras)):
                if re.search(npat, paras[j]):
                    nxt = j
                    break
        end = nxt if nxt is not None else len(paras)
        out.append('\n'.join(paras[found:end]))
        pi = found + 1
    return out


def tidy(s: str) -> str:
    s = s.replace('\u00a0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n *', ' ', s)
    s = re.sub(r'([.!?…»”])(["“]?[A-ZА-ЯЁ])', r'\1 \2', s)
    s = re.sub(r'([а-яё])([A-Z])', r'\1 \2', s)
    s = re.sub(r'([a-z.])(«)', r'\1 \2', s)
    s = re.sub(r'([.!?])«', r'\1 «', s)
    s = re.sub(r' {2,}', ' ', s)
    return s.replace(' .', '.').strip()


def _cyr_ratio(s: str) -> float:
    letters = re.findall(r'[A-Za-zА-Яа-яЁё]', s)
    if not letters:
        return 0.0
    cyr = sum(1 for ch in letters if re.match(r'[А-Яа-яЁё]', ch))
    return cyr / len(letters)


def split_lang(raw: str) -> tuple[str, str, str]:
    text = tidy(raw)
    en_start = None
    for match in re.finditer(r'[A-Z][a-z]{2,}', text):
        window = text[match.start() : match.start() + 90]
        if _cyr_ratio(window) > 0.12:
            continue
        before = text[max(0, match.start() - 2) : match.start()]
        if before and not re.search(r'[\s.!?»“"“-]', before[-1]):
            continue
        en_start = match.start()
        break
    if en_start is None:
        ru, rest = text, ''
    else:
        ru, rest = text[:en_start].strip(), text[en_start:].strip()
    candidates = []
    mark = re.search(r"[oOgG][‘’ʻ']", rest)
    if mark:
        candidates.append(mark.start())
    quote = re.search(r'\s«[A-Za-z]', rest)
    if quote and quote.start() > 40:
        candidates.append(quote.start() + 1)
    named = re.search(
        r'\s(?:Yamchan|Ushbu|Nori chips —|Soya sousi|Sous )\b',
        rest,
    )
    if named and named.start() > 40:
        candidates.append(named.start() + 1)
    if candidates:
        cut_at = min(candidates)
        idx = max(
            rest.rfind('. ', 0, cut_at),
            rest.rfind('! ', 0, cut_at),
            rest.rfind('? ', 0, cut_at),
        )
        start = idx + 2 if idx >= 0 else cut_at
        if start > cut_at:
            start = cut_at
        en, uz = rest[:start].strip(), rest[start:].strip()
    else:
        en, uz = rest, ''
    en = en.replace(
        'Unagi sauce is a fallback option in Japanese cuisine.',
        'Unagi sauce is traditional in Japanese cuisine.',
    )
    return ru, en, uz


def main() -> int:
    docx = Path(sys.argv[1] if len(sys.argv) > 1 else '')
    if not docx.is_file():
        docx = Path('/Users/olegbonislavskyi/Downloads/Карточки_товаров.docx')
    paras = docx_paragraphs(docx)
    chunks = chunks_from_paras(paras)
    rows = json.loads(CATALOG_JSON.read_text(encoding='utf-8'))
    if len(rows) != len(chunks):
        raise SystemExit(f'count mismatch json={len(rows)} chunks={len(chunks)}')
    for row, chunk in zip(rows, chunks):
        ru, en, uz = split_lang(chunk)
        row['description'] = ru
        row['description_ru'] = ru
        row['description_en'] = en
        row['description_uz'] = uz
        print(f"{row['slug']}: ru={len(ru)} en={len(en)} uz={len(uz)}")
    CATALOG_JSON.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    print(f'Wrote {CATALOG_JSON}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
