from pathlib import Path

from pypdf import PdfReader

from ancientbook.cli import build_parser, main


def test_cli_help_describes_document_inputs():
    help_text = build_parser().format_help()

    assert "documents to render" in help_text
    for extension in [".txt", ".md", ".docx", ".pdf", ".rtf", ".html", ".odt"]:
        assert extension in help_text


def test_cli_generates_pdf(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    exit_code = main([str(source), "--output", str(output), "--overwrite"])

    assert exit_code == 0
    assert output.exists()
    assert output.stat().st_size > 1000


def test_cli_accepts_layout_flags(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    exit_code = main(
        [
            str(source),
            "--output",
            str(output),
            "--overwrite",
            "--template",
            "classic",
            "--paper-size",
            "a5",
            "--font-size",
            "large",
            "--columns",
            "fewer",
        ]
    )

    reader = PdfReader(str(output))
    assert exit_code == 0
    assert float(reader.pages[0].mediabox.width) == 420
    assert float(reader.pages[0].mediabox.height) == 595
