from __future__ import annotations

import argparse
from pathlib import Path

from ancientbook.app_service import FriendlyGenerationError, GenerateRequest, generate_pdf_from_request
from ancientbook.presets import COLUMN_DENSITY_CHOICES, FONT_SIZE_CHOICES, PAPER_SIZE_CHOICES, TEMPLATE_CHOICES


def _choice_keys(choices):
    return [choice.key for choice in choices]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an ancient-book-style vertical PDF.")
    parser.add_argument(
        "document_files",
        nargs="+",
        help="documents to render (.txt, .md, .docx, .pdf, .rtf, .html, .odt; .doc must be saved as .docx first)",
    )
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--font", default=None, help="Optional local .ttf or .otf font path")
    parser.add_argument("--title", default="AncientBook", help="PDF title")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output PDF if it exists")
    parser.add_argument("--template", choices=_choice_keys(TEMPLATE_CHOICES), default="simple", help="Background template")
    parser.add_argument("--paper-size", choices=_choice_keys(PAPER_SIZE_CHOICES), default="a4", help="Paper size")
    parser.add_argument("--font-size", choices=_choice_keys(FONT_SIZE_CHOICES), default="medium", help="Font size preset")
    parser.add_argument("--columns", choices=_choice_keys(COLUMN_DENSITY_CHOICES), default="standard", help="Column density")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        generate_pdf_from_request(
            GenerateRequest(
                text_files=[Path(path) for path in args.document_files],
                output_path=Path(args.output),
                font_path=Path(args.font) if args.font else None,
                title=args.title,
                overwrite=args.overwrite,
                template_key=args.template,
                paper_size=args.paper_size,
                font_size=args.font_size,
                columns=args.columns,
            )
        )
    except FriendlyGenerationError as exc:
        parser.exit(2, f"AncientBook error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
