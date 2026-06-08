from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from reportlab.pdfgen import canvas
from pypdf import PdfReader

from ancientbook.app_service import FriendlyGenerationError, GenerateRequest, GenerateResult, generate_pdf_from_request


def test_generate_pdf_from_request_creates_pdf(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    result = generate_pdf_from_request(
        GenerateRequest(text_files=[source], output_path=output, overwrite=True)
    )

    assert isinstance(result, GenerateResult)
    assert result.output_path == output
    assert output.exists()
    assert output.stat().st_size > 1000


def test_generate_pdf_from_request_requires_document_files(tmp_path: Path):
    output = tmp_path / "sample.pdf"

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[], output_path=output))

    assert "请选择至少一个文档文件" in str(exc.value)


def test_generate_pdf_from_request_requires_pdf_extension(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("天地", encoding="utf-8")

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=tmp_path / "sample.txt"))

    assert "输出文件需要以 .pdf 结尾" in str(exc.value)


def test_generate_pdf_from_request_rejects_missing_document_file_with_friendly_message(tmp_path: Path):
    output = tmp_path / "sample.pdf"
    missing = tmp_path / "missing.txt"

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[missing], output_path=output))

    assert "找不到这个文档文件" in str(exc.value)


def test_generate_pdf_from_request_rejects_missing_output_path_with_friendly_message(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("天地", encoding="utf-8")

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=Path("")))

    assert "请选择 PDF 保存位置" in str(exc.value)


def test_generate_pdf_from_request_rejects_missing_output_directory(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("天地", encoding="utf-8")
    output = tmp_path / "missing" / "sample.pdf"

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=output))

    assert "PDF 保存目录不存在" in str(exc.value)


def test_generate_pdf_from_request_uses_layout_choices(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    result = generate_pdf_from_request(
        GenerateRequest(
            text_files=[source],
            output_path=output,
            overwrite=True,
            template_key="aged",
            paper_size="a5",
            font_size="large",
            columns="fewer",
        )
    )

    reader = PdfReader(str(output))
    assert result.page_count == 1
    assert float(reader.pages[0].mediabox.width) == 420
    assert float(reader.pages[0].mediabox.height) == 595


def test_generate_pdf_from_request_accepts_docx_input(tmp_path: Path):
    source = tmp_path / "sample.docx"
    output = tmp_path / "sample.pdf"
    _write_minimal_docx(source, "天地玄黃，宇宙洪荒。")

    result = generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=output, overwrite=True))

    assert result.output_path == output
    assert output.exists()


def test_generate_pdf_from_request_rejects_legacy_doc_with_friendly_message(tmp_path: Path):
    source = tmp_path / "sample.doc"
    output = tmp_path / "sample.pdf"
    source.write_bytes(b"\xd0\xcf\x11\xe0")

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=output))

    assert "请先把 .doc 另存为 .docx" in str(exc.value)


def test_generate_pdf_from_request_rejects_scanned_pdf_with_friendly_message(tmp_path: Path):
    source = tmp_path / "scan.pdf"
    output = tmp_path / "sample.pdf"
    drawing = canvas.Canvas(str(source))
    drawing.showPage()
    drawing.save()

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=output))

    assert "PDF 没有可复制文字" in str(exc.value)


def _write_minimal_docx(path: Path, *paragraphs: str) -> None:
    body = "".join(f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>" for paragraph in paragraphs)
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        archive.writestr(
            "word/document.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
            <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
              <w:body>{body}</w:body>
            </w:document>""",
        )
