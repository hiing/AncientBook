from __future__ import annotations

from collections.abc import Callable

from PIL import Image, ImageDraw

from ancientbook.model import LayoutSettings
from ancientbook.presets import TEMPLATE_CHOICES


PAPER_COLOR = (247, 239, 218)
AGED_PAPER_COLOR = (236, 222, 190)
INK_LINE_COLOR = (86, 58, 38)
SOFT_INK_LINE_COLOR = (135, 101, 73)
VERMILION = (151, 45, 34)
LIGHT_VERMILION = (185, 88, 65)
FIBER_COLOR = (226, 213, 184)
WATER_STAIN = (217, 197, 158)


def _draw_paper_texture(image: Image.Image, base: tuple[int, int, int], strength: int) -> None:
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        band = ((y * 7) % 19) - 9
        for x in range(width):
            grain = ((x * 17 + y * 31 + (x * y) % 13) % (strength * 2 + 1)) - strength
            tone = max(-strength, min(strength, grain + band // 4))
            pixels[x, y] = tuple(max(0, min(255, channel + tone)) for channel in base)


def _draw_basic_frame(image: Image.Image, settings: LayoutSettings, line_color: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(image)

    left = settings.margin // 2
    top = settings.margin // 2
    right = settings.page_width - settings.margin // 2
    bottom = settings.page_height - settings.margin // 2

    draw.rectangle((left, top, right, bottom), outline=line_color, width=2)
    draw.rectangle(
        (settings.margin, settings.margin, settings.page_width - settings.margin, settings.page_height - settings.margin),
        outline=line_color,
        width=1,
    )

    center_x = settings.page_width // 2
    draw.line((center_x, top, center_x, bottom), fill=line_color, width=1)


def _draw_corner_brackets(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
    left, top, right, bottom = box
    length = 22
    for x1, y1, x2, y2 in [
        (left, top + length, left, top),
        (left, top, left + length, top),
        (right - length, top, right, top),
        (right, top, right, top + length),
        (left, bottom - length, left, bottom),
        (left, bottom, left + length, bottom),
        (right - length, bottom, right, bottom),
        (right, bottom, right, bottom - length),
    ]:
        draw.line((x1, y1, x2, y2), fill=color, width=2)


def _corner_decoration_box(settings: LayoutSettings) -> tuple[int, int, int, int]:
    inset = max(1, settings.margin - 18)
    return (inset, inset, settings.page_width - inset, settings.page_height - inset)


def _draw_vertical_column_guides(image: Image.Image, settings: LayoutSettings, color: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(image)
    top = settings.margin
    bottom = settings.page_height - settings.margin
    for index in range(settings.columns + 1):
        x = settings.page_width - settings.margin - index * settings.column_width
        draw.line((x, top, x, bottom), fill=color, width=1)


def _draw_subtle_fibers(image: Image.Image, settings: LayoutSettings) -> None:
    draw = ImageDraw.Draw(image)
    for y in range(18, settings.page_height, 31):
        offset = (y * 11) % 29
        draw.line((offset, y, settings.page_width - offset // 2, y + ((y // 31) % 3) - 1), fill=FIBER_COLOR, width=1)
    for x in range(28, settings.page_width, 47):
        top = (x * 5) % 43
        draw.line((x, top, x + ((x // 47) % 3) - 1, settings.page_height - top), fill=(232, 221, 195), width=1)


def _draw_soft_stains(image: Image.Image, settings: LayoutSettings) -> None:
    draw = ImageDraw.Draw(image)
    stains = [
        (settings.margin // 2, settings.margin // 3, settings.margin * 2, settings.margin + 36),
        (settings.page_width - settings.margin * 2, settings.page_height - settings.margin * 2, settings.page_width - 20, settings.page_height - 18),
        (settings.page_width // 5, settings.page_height // 2, settings.page_width // 5 + 70, settings.page_height // 2 + 34),
    ]
    for box in stains:
        draw.ellipse(box, outline=WATER_STAIN, width=1)


def create_simple_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), PAPER_COLOR)
    _draw_paper_texture(image, PAPER_COLOR, strength=3)
    _draw_subtle_fibers(image, settings)
    _draw_basic_frame(image, settings, INK_LINE_COLOR)
    draw = ImageDraw.Draw(image)
    _draw_corner_brackets(draw, _corner_decoration_box(settings), SOFT_INK_LINE_COLOR)
    return image


def create_classic_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), PAPER_COLOR)
    _draw_paper_texture(image, PAPER_COLOR, strength=2)
    draw = ImageDraw.Draw(image)
    _draw_basic_frame(image, settings, VERMILION)
    decoration_box = _corner_decoration_box(settings)
    draw.rectangle(decoration_box, outline=LIGHT_VERMILION, width=1)
    _draw_vertical_column_guides(image, settings, (213, 160, 132))
    _draw_corner_brackets(draw, decoration_box, VERMILION)
    return image


def create_aged_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), AGED_PAPER_COLOR)
    _draw_paper_texture(image, AGED_PAPER_COLOR, strength=8)
    draw = ImageDraw.Draw(image)
    for y in range(0, settings.page_height, 18):
        tone = (224, 207, 170) if y % 36 == 0 else (241, 229, 200)
        draw.line((0, y, settings.page_width, y), fill=tone, width=1)
    _draw_subtle_fibers(image, settings)
    _draw_soft_stains(image, settings)
    _draw_basic_frame(image, settings, SOFT_INK_LINE_COLOR)
    decoration_box = _corner_decoration_box(settings)
    draw.rectangle(decoration_box, outline=(157, 115, 78), width=1)
    _draw_corner_brackets(draw, decoration_box, (112, 76, 49))
    return image


_TEMPLATE_BUILDERS: dict[str, Callable[[LayoutSettings], Image.Image]] = {
    "simple": create_simple_background,
    "classic": create_classic_background,
    "aged": create_aged_background,
}


def template_keys() -> list[str]:
    return [choice.key for choice in TEMPLATE_CHOICES]


def template_labels() -> list[str]:
    return [choice.label for choice in TEMPLATE_CHOICES]


def create_background(template_key: str, settings: LayoutSettings) -> Image.Image:
    builder = _TEMPLATE_BUILDERS.get(template_key, create_simple_background)
    return builder(settings)
