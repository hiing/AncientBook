from __future__ import annotations

from PIL import Image, ImageDraw
from PySide6.QtGui import QImage, QPixmap

from ancientbook.model import LayoutSettings
from ancientbook.presets import build_layout_settings
from ancientbook.template import create_background


INK = (43, 32, 24)
SOFT_INK = (82, 62, 46)


def _draw_preview_text(image: Image.Image, settings: LayoutSettings) -> None:
    draw = ImageDraw.Draw(image)
    top = settings.margin + 32
    max_columns = min(settings.columns, 9)
    max_rows = min(settings.rows, 13)

    for column_index in range(max_columns):
        x = settings.page_width - settings.margin - column_index * settings.column_width - settings.column_width // 2
        if x <= settings.margin:
            continue
        column_offset = (column_index * 5) % 17
        for row_index in range(0, max_rows, 2):
            y = top + row_index * settings.row_height + column_offset
            length = max(settings.font_size + 12, settings.row_height - 4)
            if y + length >= settings.page_height - settings.margin:
                continue
            color = INK if row_index % 4 == 0 else SOFT_INK
            draw.rounded_rectangle((x - 2, y, x + 2, y + length), radius=2, fill=color)


def create_preview_image(
    template_key: str,
    paper_size: str,
    font_size: str,
    columns: str,
    max_height: int = 430,
) -> Image.Image:
    settings = build_layout_settings(paper_size=paper_size, font_size=font_size, columns=columns)
    image = create_background(template_key, settings)
    _draw_preview_text(image, settings)

    preview = image.copy()
    preview.thumbnail((max_height, max_height), Image.Resampling.LANCZOS)
    return preview.convert("RGB")


def pixmap_from_image(image: Image.Image) -> QPixmap:
    rgba = image.convert("RGBA")
    data = rgba.tobytes("raw", "RGBA")
    qimage = QImage(
        data,
        rgba.width,
        rgba.height,
        rgba.width * 4,
        QImage.Format.Format_RGBA8888,
    )
    return QPixmap.fromImage(qimage.copy())
