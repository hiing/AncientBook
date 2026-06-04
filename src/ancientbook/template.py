from __future__ import annotations

from PIL import Image, ImageDraw

from ancientbook.model import LayoutSettings


PAPER_COLOR = (244, 236, 216)
LINE_COLOR = (86, 58, 38)


def create_simple_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), PAPER_COLOR)
    draw = ImageDraw.Draw(image)

    left = settings.margin // 2
    top = settings.margin // 2
    right = settings.page_width - settings.margin // 2
    bottom = settings.page_height - settings.margin // 2

    draw.rectangle((left, top, right, bottom), outline=LINE_COLOR, width=2)
    draw.rectangle(
        (settings.margin, settings.margin, settings.page_width - settings.margin, settings.page_height - settings.margin),
        outline=LINE_COLOR,
        width=1,
    )

    center_x = settings.page_width // 2
    draw.line((center_x, top, center_x, bottom), fill=LINE_COLOR, width=1)
    return image
