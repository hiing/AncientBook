from pathlib import Path

import pytest

from ancientbook.text_reader import TextReadError, read_text_files


def test_read_text_files_merges_utf8_files(tmp_path: Path):
    first = tmp_path / "001.txt"
    second = tmp_path / "002.txt"
    first.write_text("天地玄黃", encoding="utf-8")
    second.write_text("宇宙洪荒", encoding="utf-8")

    assert read_text_files([first, second]) == "天地玄黃\n宇宙洪荒"


def test_read_text_files_removes_unsupported_control_characters(tmp_path: Path):
    source = tmp_path / "book.txt"
    source.write_text("天\u0000地\t玄\n黃", encoding="utf-8")

    assert read_text_files([source]) == "天地\t玄\n黃"


def test_read_text_files_reports_missing_file(tmp_path: Path):
    missing = tmp_path / "missing.txt"

    with pytest.raises(TextReadError) as exc:
        read_text_files([missing])

    assert "Cannot read text file" in str(exc.value)
