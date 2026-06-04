from pathlib import Path

import pytest
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


def test_generate_pdf_from_request_requires_text_files(tmp_path: Path):
    output = tmp_path / "sample.pdf"

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[], output_path=output))

    assert "请选择至少一个文本文件" in str(exc.value)


def test_generate_pdf_from_request_requires_pdf_extension(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("天地", encoding="utf-8")

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=tmp_path / "sample.txt"))

    assert "输出文件需要以 .pdf 结尾" in str(exc.value)


def test_generate_pdf_from_request_rejects_missing_text_file_with_friendly_message(tmp_path: Path):
    output = tmp_path / "sample.pdf"
    missing = tmp_path / "missing.txt"

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[missing], output_path=output))

    assert "找不到这个文本文件" in str(exc.value)


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
