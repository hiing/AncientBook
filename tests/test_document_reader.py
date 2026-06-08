from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from reportlab.pdfgen import canvas

from ancientbook.document_reader import DocumentReadError, read_document_files


def test_read_document_files_merges_txt_and_markdown(tmp_path: Path):
    plain = tmp_path / "plain.txt"
    markdown = tmp_path / "notes.md"
    plain.write_text("天地玄黃", encoding="utf-8")
    markdown.write_text("# 宇宙洪荒\n\n- 日月盈昃\n\n[辰宿](https://example.com)列張", encoding="utf-8")

    text = read_document_files([plain, markdown])

    assert text == "天地玄黃\n宇宙洪荒\n日月盈昃\n辰宿列張"


def test_read_document_files_extracts_docx_text(tmp_path: Path):
    docx = tmp_path / "book.docx"
    _write_minimal_docx(docx, "天地玄黃", "宇宙洪荒")

    assert read_document_files([docx]) == "天地玄黃\n宇宙洪荒"


def test_read_document_files_extracts_selectable_pdf_text(tmp_path: Path):
    pdf = tmp_path / "book.pdf"
    drawing = canvas.Canvas(str(pdf))
    drawing.drawString(72, 720, "Heaven Earth")
    drawing.drawString(72, 700, "Ancient Book")
    drawing.save()

    text = read_document_files([pdf])

    assert "Heaven Earth" in text
    assert "Ancient Book" in text


def test_read_document_files_rejects_scanned_or_blank_pdf(tmp_path: Path):
    pdf = tmp_path / "blank.pdf"
    drawing = canvas.Canvas(str(pdf))
    drawing.showPage()
    drawing.save()

    with pytest.raises(DocumentReadError) as exc:
        read_document_files([pdf])

    assert "PDF has no selectable text" in str(exc.value)


def test_read_document_files_extracts_basic_rtf_text(tmp_path: Path):
    rtf = tmp_path / "book.rtf"
    rtf.write_text(r"{\rtf1\ansi \u22825?\u22320?\par \u29572?\u40643?}", encoding="utf-8")

    assert read_document_files([rtf]) == "天地\n玄黃"


def test_read_document_files_extracts_html_text(tmp_path: Path):
    html = tmp_path / "book.html"
    html.write_text("<h1>天地玄黃</h1><p>宇宙<br>洪荒</p>", encoding="utf-8")

    assert read_document_files([html]) == "天地玄黃\n宇宙\n洪荒"


def test_read_document_files_extracts_odt_text(tmp_path: Path):
    odt = tmp_path / "book.odt"
    with ZipFile(odt, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "content.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
              <office:body>
                <office:text>
                  <text:p>天地玄黃</text:p>
                  <text:p>宇宙洪荒</text:p>
                </office:text>
              </office:body>
            </office:document-content>""",
        )

    assert read_document_files([odt]) == "天地玄黃\n宇宙洪荒"


def test_read_document_files_rejects_legacy_doc_with_friendly_hint(tmp_path: Path):
    legacy_doc = tmp_path / "old.doc"
    legacy_doc.write_bytes(b"\xd0\xcf\x11\xe0")

    with pytest.raises(DocumentReadError) as exc:
        read_document_files([legacy_doc])

    assert "Please save .doc as .docx" in str(exc.value)


def _write_minimal_docx(path: Path, *paragraphs: str) -> None:
    body = "".join(f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>" for paragraph in paragraphs)
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
            <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
              <Default Extension="xml" ContentType="application/xml"/>
              <Override PartName="/word/document.xml"
                ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
            </Types>""",
        )
        archive.writestr(
            "word/document.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>{body}</w:body>
            </w:document>""",
        )
