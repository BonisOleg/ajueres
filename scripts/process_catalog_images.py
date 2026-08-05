"""Build transparent Sen Soy catalog assets from approved source photos."""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / 'content' / 'products'
STATIC_DIR = ROOT / 'static' / 'img' / 'catalog'
CANVAS_SIZE = 1000
OBJECT_LIMIT = 880
BACKGROUND_DISTANCE = 15

PRODUCTS = {
    '4607041132712.png': (
        'sen-soy-лапша-somen-300-гр.png',
        ('sen-soy-0ce9a674a7.png', 'sen-soy-fa0cf8c2d3.png'),
    ),
    '4607041136949.webp': (
        'sen-soy-соус-сладкий-чили-235-гр.png',
        ('sen-soy-7e17cb1c9c.png',),
    ),
    '4607041137229.webp': (
        'sen-soy-соус-шрирача-310-гр.png',
        ('sen-soy-cb449d64ec.png', 'sen-soy-5e9fa95fed.png'),
    ),
    '4607041133320.jpeg': (
        'sen-soy-суши-нори-28-гр.png',
        ('sen-soy-0c2ba9e0b7.png', 'sen-soy-3554559a90.png'),
    ),
    '4607041133795.jpg': (
        'sen-soy-чипсы-нори-original-45-гр.png',
        ('sen-soy-2b6be6b0a1.png', 'sen-soy-6a3aae92b4.png'),
    ),
    '4607041136932.webp': (
        'sen-soy-соус-жгучий-чили-235-гр.png',
        ('sen-soy-b745267b30.png',),
    ),
    '4607041133054.jpg': (
        'sen-soy-соевый-соус-классический-250-гр.png',
        ('sen-soy-9690a331c6.png',),
    ),
    '4607041137700.png': (
        'sen-soy-соевый-соус-темный-220-гр.png',
        ('sen-soy-6476760b47.png',),
    ),
    '4607041133252.jpg': (
        'sen-soy-соус-сладкий-чили-манго-320-гр.png',
        ('sen-soy-fd97839ced.png',),
    ),
    '4607041136048.jpeg': (
        'sen-soy-соус-терияки-сладкий-320-гр.png',
        ('sen-soy-ea1d482ffb.png',),
    ),
    '4607041136925.jpg': (
        'sen-soy-соус-unagi-320-гр.png',
        ('sen-soy-f27cc033e3.png',),
    ),
    '4607041131753.jpg': (
        'sen-soy-соевый-соус-классический-1-л.png',
        ('sen-soy-31022b9dcb.png',),
    ),
    '4607041132705.jpeg': (
        'sen-soy-пшеничная-лапша-udon-300-гр.png',
        ('sen-soy-60180dc8b7.png',),
    ),
    '4607041132743.jpeg': (
        'sen-soy-яичная-лапша-egg-noodles-300-гр.png',
        ('sen-soy-0e57205d00.png',),
    ),
    '4607041132736.jpg': (
        'sen-soy-рисовая-лапша-rice-vermicelli-300-гр.png',
        ('sen-soy-6bcf867653.png',),
    ),
    '4607041135492.jpeg': (
        'sen-soy-рисовая-лапша-fo-kho-200-гр.png',
        ('sen-soy-91f7009e6e.png',),
    ),
    '4607041135072.webp': (
        'sen-soy-основа-для-супа-том-ям-80-гр.png',
        ('sen-soy-74c07b0d90.png',),
    ),
    '4607041133771.jpg': (
        'sen-soy-рисова-бумага-100-гр.png',
        ('sen-soy-4163f3c637.png',),
    ),
    '4607041135164.jpg': (
        'sen-soy-чипсы-нори-kimchi-45-гр.png',
        ('sen-soy-5b96b8b437.png',),
    ),
    '4607041138080.jpg': (
        'sen-soy-чипсы-нори-olive-45-гр.png',
        ('sen-soy-aff1c0dfeb.png',),
    ),
}

SOURCE_CROPS = {
    '4607041132712.png': (0, 0, 1000, 940),
}


def _distance(left: tuple[int, int, int], right: tuple[int, int, int]) -> int:
    return max(abs(left[index] - right[index]) for index in range(3))


def _background_colors(image: Image.Image) -> tuple[tuple[int, int, int], ...]:
    width, height = image.size
    radius = max(2, min(width, height) // 100)
    samples = []
    for origin_x, origin_y in (
        (0, 0),
        (width - radius, 0),
        (0, height - radius),
        (width - radius, height - radius),
    ):
        crop = image.crop((origin_x, origin_y, origin_x + radius, origin_y + radius))
        pixels = [pixel[:3] for pixel in crop.get_flattened_data() if pixel[3] > 0]
        if pixels:
            samples.append(
                tuple(sorted(pixel[channel] for pixel in pixels)[len(pixels) // 2] for channel in range(3))
            )
    return tuple(samples) or ((255, 255, 255),)


def _remove_background(image: Image.Image) -> Image.Image:
    image = image.convert('RGBA')
    width, height = image.size
    pixels = image.load()
    backgrounds = _background_colors(image)
    removed = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def is_background(x: int, y: int) -> bool:
        pixel = pixels[x, y]
        if pixel[3] == 0:
            return True
        return min(_distance(pixel[:3], background) for background in backgrounds) <= BACKGROUND_DISTANCE

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if removed[index] or not is_background(x, y):
            continue
        removed[index] = 1
        if x:
            queue.append((x - 1, y))
        if x + 1 < width:
            queue.append((x + 1, y))
        if y:
            queue.append((x, y - 1))
        if y + 1 < height:
            queue.append((x, y + 1))

    alpha = Image.new('L', image.size, 255)
    alpha_pixels = alpha.load()
    for y in range(height):
        for x in range(width):
            if removed[y * width + x]:
                alpha_pixels[x, y] = 0
    image.putalpha(alpha)
    return image


def _normalize(image: Image.Image) -> Image.Image:
    alpha = image.getchannel('A')
    bounds = alpha.getbbox()
    if not bounds:
        raise ValueError('Background removal produced an empty image')
    image = image.crop(bounds)
    scale = min(OBJECT_LIMIT / image.width, OBJECT_LIMIT / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    image = image.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    offset = ((CANVAS_SIZE - size[0]) // 2, (CANVAS_SIZE - size[1]) // 2)
    canvas.alpha_composite(image, offset)
    return canvas


def main(source_dir: Path) -> None:
    for source_name, (content_name, static_names) in PRODUCTS.items():
        source = source_dir / source_name
        if not source.is_file():
            raise FileNotFoundError(source)
        image = Image.open(source)
        if source_name in SOURCE_CROPS:
            image = image.crop(SOURCE_CROPS[source_name])
        result = _normalize(_remove_background(image))
        destinations = (CONTENT_DIR / content_name, *(STATIC_DIR / name for name in static_names))
        for destination in destinations:
            result.save(destination, 'PNG', optimize=True)
        print(f'{source_name}: {len(destinations)} asset(s)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source_dir', type=Path, help='Directory containing approved Sen Soy photos')
    arguments = parser.parse_args()
    main(arguments.source_dir.expanduser().resolve())
