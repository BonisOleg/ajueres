"""Compress static/img/catalog to WebP and drop unused PNGs.

Updates content/catalog_products.json ``static_image`` fields.
Keeps content/products/ originals untouched (local seed / Vercel-ignored).
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CATALOG_JSON = ROOT / 'content' / 'catalog_products.json'
STATIC_DIR = ROOT / 'static' / 'img' / 'catalog'
MAX_SIDE = 800
WEBP_QUALITY = 78


def _to_webp(source: Path) -> bytes:
    image = Image.open(source)
    if image.mode not in ('RGB', 'L'):
        image = image.convert('RGB')
    elif image.mode == 'L':
        image = image.convert('RGB')
    image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format='WEBP', quality=WEBP_QUALITY, method=4)
    return buffer.getvalue()


def _static_name(brand: str, payload: bytes) -> str:
    digest = hashlib.md5(payload).hexdigest()[:10]
    return f'{brand}-{digest}.webp'


def main() -> None:
    rows = json.loads(CATALOG_JSON.read_text(encoding='utf-8'))
    keep_names: set[str] = set()
    before = 0
    after = 0

    for row in rows:
        old_name = row.get('static_image') or ''
        old_path = STATIC_DIR / old_name
        # Fallback: content original if static missing
        content_name = row.get('image') or ''
        content_path = ROOT / 'content' / 'products' / content_name
        source = old_path if old_path.is_file() else content_path
        if not source.is_file():
            raise SystemExit(f'Missing image for {row.get("slug")}: {source}')

        before += source.stat().st_size
        payload = _to_webp(source)
        after += len(payload)
        brand = (row.get('brand') or 'product').strip() or 'product'
        new_name = _static_name(brand, payload)
        (STATIC_DIR / new_name).write_bytes(payload)
        row['static_image'] = new_name
        keep_names.add(new_name)

    CATALOG_JSON.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    removed = 0
    removed_bytes = 0
    for path in STATIC_DIR.iterdir():
        if not path.is_file():
            continue
        if path.name in keep_names:
            continue
        removed_bytes += path.stat().st_size
        path.unlink()
        removed += 1

    print(
        f'webp: {before / 1e6:.1f} MB → {after / 1e6:.1f} MB; '
        f'removed {removed} unused files ({removed_bytes / 1e6:.1f} MB); '
        f'kept {len(keep_names)}'
    )


if __name__ == '__main__':
    main()
