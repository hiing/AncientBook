from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from ancientbook.model import GlyphPlacement, LayoutSettings
from ancientbook.presets import DEFAULT_TEMPLATE
from ancientbook.system_fonts import available_font_choices
from ancientbook.template import create_background


class PdfGenerationError(RuntimeError):
    pass


def default_font_path() -> Path | None:
    for choice in available_font_choices():
        if choice.path is not None:
            return choice.path
    return None


def _register_font(font_path: Path | None) -> str:
    if font_path is None:
        font_path = default_font_path()
    if font_path is None:
        return "Helvetica"
    path = Path(font_path)
    if not path.exists():
        raise PdfGenerationError(f"Font file does not exist: {path}")
    font_name = f"AncientBookFont-{abs(hash(path))}"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(path)))
    return font_name


def _background_reader(settings: LayoutSettings, template_key: str) -> ImageReader:
    image = create_background(template_key, settings)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer)


def _draw_placement(pdf, placement: GlyphPlacement, font_name: str) -> None:
    pdf.setFont(font_name, placement.font_size)
    pdf.drawCentredString(placement.x, placement.y, placement.text)


def write_pdf(
    output_path: Path,
    placements: list[GlyphPlacement],
    settings: LayoutSettings,
    font_path: Path | None,
    title: str,
    overwrite: bool = False,
    template_key: str = DEFAULT_TEMPLATE,
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

    background = _background_reader(settings, template_key)
    for page_index in range(page_count):
        pdf.drawImage(background, 0, 0, width=settings.page_width, height=settings.page_height)
        for placement in placements:
            if placement.page_index != page_index:
                continue
            _draw_placement(pdf, placement, font_name)
        pdf.showPage()
    pdf.save()
