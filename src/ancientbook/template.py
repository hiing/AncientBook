from __future__ import annotations

from collections.abc import Callable

from PIL import Image, ImageDraw

from ancientbook.model import LayoutSettings
from ancientbook.presets import TEMPLATE_CHOICES


PAPER_COLOR = (244, 236, 216)
AGED_PAPER_COLOR = (238, 226, 198)
LINE_COLOR = (86, 58, 38)
LIGHT_LINE_COLOR = (136, 102, 74)


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


def create_simple_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), PAPER_COLOR)
    _draw_basic_frame(image, settings, LINE_COLOR)
    return image


def create_classic_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), PAPER_COLOR)
    draw = ImageDraw.Draw(image)
    _draw_basic_frame(image, settings, LINE_COLOR)
    inset = settings.margin + 12
    draw.rectangle(
        (inset, inset, settings.page_width - inset, settings.page_height - inset),
        outline=LINE_COLOR,
        width=1,
    )
    return image


def create_aged_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), AGED_PAPER_COLOR)
    draw = ImageDraw.Draw(image)
    for y in range(0, settings.page_height, 18):
        tone = (232, 217, 188) if y % 36 == 0 else (242, 231, 205)
        draw.line((0, y, settings.page_width, y), fill=tone, width=1)
    _draw_basic_frame(image, settings, LIGHT_LINE_COLOR)
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
