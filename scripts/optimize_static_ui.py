"""Convert homepage UI rasters to sized WebP. Run once, commit results.

Does not touch static/img/catalog (see optimize_catalog_webp.py).
Keeps logo-ajeres.png for Open Graph.
"""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / 'static' / 'img'
WEBP_QUALITY = 80
LOGO_KEEP_PNG = IMG / 'logo-ajeres.png'


def _has_alpha(image: Image.Image) -> bool:
    if image.mode in {'RGBA', 'LA', 'PA'}:
        return True
    return image.mode == 'P' and 'transparency' in image.info


def _prepare(image: Image.Image) -> Image.Image:
    if _has_alpha(image):
        return image.convert('RGBA')
    if image.mode == 'L':
        return image.convert('RGB')
    if image.mode != 'RGB':
        return image.convert('RGB')
    return image


def _save_webp(image: Image.Image, dest: Path) -> int:
    prepared = _prepare(image)
    buffer = io.BytesIO()
    prepared.save(buffer, format='WEBP', quality=WEBP_QUALITY, method=4)
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = buffer.getvalue()
    dest.write_bytes(payload)
    return len(payload)


def _open(source: Path) -> Image.Image:
    image = Image.open(source)
    image.load()
    return image


def _fit(image: Image.Image, max_width: int | None = None, max_side: int | None = None) -> Image.Image:
    copy = image.copy()
    if max_width is not None and copy.size[0] > max_width:
        ratio = max_width / copy.size[0]
        copy.thumbnail((max_width, max(1, int(copy.size[1] * ratio))), Image.Resampling.LANCZOS)
        return copy
    if max_side is not None:
        copy.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return copy


def _convert_variants(source: Path, jobs: list[tuple[Path, dict]]) -> None:
    if not source.is_file():
        missing = [dest for dest, _opts in jobs if not dest.is_file()]
        if missing:
            raise SystemExit(f'Missing source {source} and dest {missing[0]}')
        print(f'skip (no source, dest exists): {source.name}')
        return
    image = _open(source)
    before = source.stat().st_size
    after = 0
    for dest, opts in jobs:
        sized = _fit(image, max_width=opts.get('max_width'), max_side=opts.get('max_side'))
        after += _save_webp(sized, dest)
        print(f'  {dest.relative_to(ROOT)} {sized.size[0]}x{sized.size[1]} {after and ""}')
    if source != LOGO_KEEP_PNG:
        source.unlink()
        print(f'  removed {source.name} ({before / 1024:.0f} KiB) → {after / 1024:.0f} KiB')
    else:
        print(f'  kept {source.name} for OG; webp {after / 1024:.0f} KiB')


def _convert_dir(folder: Path, max_side: int) -> None:
    if not folder.is_dir():
        return
    for path in sorted(folder.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
            continue
        dest = path.with_suffix('.webp')
        image = _open(path)
        sized = _fit(image, max_side=max_side)
        after = _save_webp(sized, dest)
        before = path.stat().st_size
        path.unlink()
        print(
            f'  {dest.relative_to(ROOT)} {sized.size[0]}x{sized.size[1]} '
            f'{before / 1024:.0f}→{after / 1024:.0f} KiB'
        )


def main() -> None:
    print('hero')
    _convert_variants(
        IMG / 'hero-samarkand.png',
        [
            (IMG / 'hero-samarkand-640.webp', {'max_width': 640}),
            (IMG / 'hero-samarkand.webp', {'max_width': 1024}),
        ],
    )
    print('footer skyline')
    _convert_variants(
        IMG / 'footer-samarkand-silhouette.png',
        [
            (IMG / 'footer-samarkand-silhouette-800.webp', {'max_width': 800}),
            (IMG / 'footer-samarkand-silhouette-1440.webp', {'max_width': 1440}),
        ],
    )
    print('fingerprint')
    _convert_variants(
        IMG / 'fingerprint-white.png',
        [(IMG / 'fingerprint-white.webp', {'max_side': 52})],
    )
    print('paper grain')
    _convert_variants(
        IMG / 'paper-grain-soft.png',
        [(IMG / 'paper-grain-soft.webp', {'max_side': 256})],
    )
    print('logo')
    _convert_variants(
        IMG / 'logo-ajeres.png',
        [
            (IMG / 'logo-ajeres-196.webp', {'max_width': 196}),
            (IMG / 'logo-ajeres.webp', {'max_width': 392}),
        ],
    )
    print('partners')
    _convert_dir(IMG / 'partners', max_side=460)
    print('brands')
    _convert_dir(IMG / 'brands', max_side=460)


if __name__ == '__main__':
    main()
