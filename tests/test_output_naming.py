from pathlib import Path

from ancientbook import output_naming
from ancientbook.output_naming import default_output_path


def test_default_output_path_uses_selected_folder_and_first_text_name(tmp_path: Path):
    text_file = tmp_path / "texts" / "sample.txt"
    output_dir = tmp_path / "out"

    output = default_output_path([text_file], output_dir)

    assert output == output_dir / "sample-AncientBook.pdf"


def test_default_output_path_uses_text_folder_when_output_folder_is_missing(tmp_path: Path):
    text_file = tmp_path / "texts" / "sample.txt"

    output = default_output_path([text_file], None)

    assert output == text_file.parent / "sample-AncientBook.pdf"


def test_default_output_path_falls_back_when_no_text_file_is_selected(tmp_path: Path):
    output = default_output_path([], tmp_path)

    assert output == tmp_path / "AncientBook.pdf"


def test_unique_output_path_adds_number_when_pdf_exists(tmp_path: Path):
    existing = tmp_path / "sample-AncientBook.pdf"
    existing.write_text("existing", encoding="utf-8")

    output = output_naming.unique_output_path(existing)

    assert output == tmp_path / "sample-AncientBook-2.pdf"


def test_unique_output_path_skips_existing_numbered_pdf(tmp_path: Path):
    (tmp_path / "sample-AncientBook.pdf").write_text("existing", encoding="utf-8")
    (tmp_path / "sample-AncientBook-2.pdf").write_text("existing", encoding="utf-8")

    output = output_naming.unique_output_path(tmp_path / "sample-AncientBook.pdf")

    assert output == tmp_path / "sample-AncientBook-3.pdf"
