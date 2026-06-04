from pathlib import Path

from ancientbook.cli import main


def test_cli_generates_pdf(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    exit_code = main([str(source), "--output", str(output), "--overwrite"])

    assert exit_code == 0
    assert output.exists()
    assert output.stat().st_size > 1000
