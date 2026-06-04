from pathlib import Path

import pytest

from ancientbook.app_service import GenerateRequest, GenerateResult, generate_pdf_from_request


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

    with pytest.raises(ValueError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[], output_path=output))

    assert "Select at least one text file" in str(exc.value)


def test_generate_pdf_from_request_requires_pdf_extension(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("天地", encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=tmp_path / "sample.txt"))

    assert "Output path must end with .pdf" in str(exc.value)
