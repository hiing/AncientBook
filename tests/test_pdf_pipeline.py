from pathlib import Path

from pypdf import PdfReader

from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.model import LayoutSettings
from ancientbook.pdf import PdfGenerationError, write_pdf


def test_write_pdf_creates_readable_pdf(tmp_path: Path):
    output = tmp_path / "book.pdf"
    settings = LayoutSettings(page_width=300, page_height=400, margin=40, columns=4, rows=6, font_size=14)
    tokens = parse_markup("天地玄黃")
    placements = layout_tokens(tokens, settings)

    write_pdf(output, placements, settings, font_path=None, title="Test Book")

    reader = PdfReader(str(output))
    assert len(reader.pages) == 1
    assert output.stat().st_size > 1000


def test_write_pdf_refuses_to_overwrite_without_flag(tmp_path: Path):
    output = tmp_path / "book.pdf"
    output.write_bytes(b"existing")
    settings = LayoutSettings(page_width=300, page_height=400)

    try:
        write_pdf(output, [], settings, font_path=None, title="Test Book")
    except PdfGenerationError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("Expected PdfGenerationError")
