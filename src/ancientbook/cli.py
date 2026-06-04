from __future__ import annotations

import argparse
from pathlib import Path

from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.model import LayoutSettings
from ancientbook.pdf import PdfGenerationError, write_pdf
from ancientbook.text_reader import TextReadError, read_text_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an ancient-book-style vertical PDF.")
    parser.add_argument("text_files", nargs="+", help="UTF-8 .txt files to render")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--font", default=None, help="Optional local .ttf or .otf font path")
    parser.add_argument("--title", default="AncientBook", help="PDF title")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output PDF if it exists")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = read_text_files([Path(path) for path in args.text_files])
        tokens = parse_markup(text)
        settings = LayoutSettings()
        placements = layout_tokens(tokens, settings)
        font_path = Path(args.font) if args.font else None
        write_pdf(Path(args.output), placements, settings, font_path, args.title, overwrite=args.overwrite)
    except (TextReadError, PdfGenerationError) as exc:
        parser.exit(2, f"AncientBook error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
