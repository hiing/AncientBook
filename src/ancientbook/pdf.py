from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from ancientbook.model import GlyphPlacement, LayoutSettings
from ancientbook.template import create_simple_background


class PdfGenerationError(RuntimeError):
    pass


def _register_font(font_path: Path | None) -> str:
    if font_path is None:
        return "Helvetica"
    path = Path(font_path)
    if not path.exists():
        raise PdfGenerationError(f"Font file does not exist: {path}")
    font_name = f"AncientBookFont-{abs(hash(path))}"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(path)))
    return font_name


def _background_reader(settings: LayoutSettings) -> ImageReader:
    image = create_simple_background(settings)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer)


def write_pdf(
    output_path: Path,
    placements: list[GlyphPlacement],
    settings: LayoutSettings,
    font_path: Path | None,
    title: str,
    overwrite: bool = False,
) -> None:
    output = Path(output_path)
    if output.exists() and not overwrite:
        raise PdfGenerationError(f"Output PDF already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    font_name = _register_font(font_path)
    page_count = max((placement.page_index for placement in placements), default=0) + 1
    pdf = canvas.Canvas(str(output), pagesize=(settings.page_width, settings.page_height))
    pdf.setTitle(title)
    pdf.setAuthor("")
    pdf.setCreator("AncientBook")

    background = _background_reader(settings)
    for page_index in range(page_count):
        pdf.drawImage(background, 0, 0, width=settings.page_width, height=settings.page_height)
        for placement in placements:
            if placement.page_index != page_index:
                continue
            pdf.setFont(font_name, placement.font_size)
            pdf.drawString(placement.x, placement.y, placement.text)
        pdf.showPage()
    pdf.save()
