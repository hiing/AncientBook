from pathlib import Path

from pypdf import PdfReader

from ancientbook import pdf
from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.model import GlyphPlacement, LayoutSettings
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


def test_write_pdf_accepts_named_template(tmp_path: Path):
    output = tmp_path / "book-aged.pdf"
    settings = LayoutSettings(page_width=300, page_height=400, margin=40, columns=4, rows=6, font_size=14)
    tokens = parse_markup("天地玄黃")
    placements = layout_tokens(tokens, settings)

    write_pdf(output, placements, settings, font_path=None, title="Test Book", template_key="aged")

    reader = PdfReader(str(output))
    assert len(reader.pages) == 1
    assert output.stat().st_size > 1000


def test_default_font_path_uses_first_system_chinese_font(monkeypatch, tmp_path: Path):
    font_file = tmp_path / "simsun.ttc"
    font_file.write_bytes(b"font")

    monkeypatch.setattr(
        "ancientbook.pdf.available_font_choices",
        lambda: [type("Choice", (), {"path": font_file})(), type("Choice", (), {"path": None})()],
    )

    assert pdf.default_font_path() == font_file


def test_draw_placement_centers_glyph_on_column_anchor():
    class RecordingPdf:
        def __init__(self):
            self.calls = []

        def setFont(self, font_name, font_size):
            self.calls.append(("setFont", font_name, font_size))

        def drawCentredString(self, x, y, text):
            self.calls.append(("drawCentredString", x, y, text))

        def drawString(self, x, y, text):
            self.calls.append(("drawString", x, y, text))

    placement = GlyphPlacement(
        page_index=0,
        column_index=0,
        row_index=0,
        x=120,
        y=240,
        text="文",
        font_size=18,
    )
    recorder = RecordingPdf()

    pdf._draw_placement(recorder, placement, "AncientBookFont")

    assert ("setFont", "AncientBookFont", 18) in recorder.calls
    assert ("drawCentredString", 120, 240, "文") in recorder.calls
    assert not any(call[0] == "drawString" for call in recorder.calls)
