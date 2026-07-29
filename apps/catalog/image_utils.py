"""Normalize catalog images: replace dark uniform backgrounds with light."""

from __future__ import annotations

from io import BytesIO

from PIL import Image

LIGHT_BG = (247, 247, 247)
_CORNER_MAX_SPREAD = 28
_LUMA_LIGHT = 210


def _luma(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def _detect_dark_uniform_bg(im: Image.Image) -> tuple[int, int, int] | None:
    rgb = im.convert('RGB')
    w, h = rgb.size
    if w < 4 or h < 4:
        return None

    corners = [
        rgb.getpixel((0, 0)),
        rgb.getpixel((w - 1, 0)),
        rgb.getpixel((0, h - 1)),
        rgb.getpixel((w - 1, h - 1)),
    ]
    avg = (
        sum(c[0] for c in corners) // 4,
        sum(c[1] for c in corners) // 4,
        sum(c[2] for c in corners) // 4,
    )
    spread = max(
        abs(c[0] - avg[0]) + abs(c[1] - avg[1]) + abs(c[2] - avg[2])
        for c in corners
    )
    if spread > _CORNER_MAX_SPREAD:
        return None
    if _luma(avg) >= _LUMA_LIGHT:
        return None
    return avg


def replace_dark_background(
    data: bytes,
    *,
    light: tuple[int, int, int] = LIGHT_BG,
    threshold: int = 40,
) -> bytes:
    """Return image bytes with a dark uniform background replaced by light."""
    source = Image.open(BytesIO(data))
    bg = _detect_dark_uniform_bg(source)
    if bg is None:
        return data

    im = source.convert('RGBA')
    lr, lg, lb = light
    br, bg_c, bb = bg
    pixels = []
    for r, g, b, a in im.getdata():
        if a == 0:
            pixels.append((lr, lg, lb, 0))
            continue
        if abs(r - br) + abs(g - bg_c) + abs(b - bb) <= threshold:
            pixels.append((lr, lg, lb, 255))
        else:
            pixels.append((r, g, b, a))

    im.putdata(pixels)
    out = BytesIO()
    im.save(out, format='PNG', optimize=True)
    return out.getvalue()
