from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.model import LayoutSettings
from ancientbook.pdf import write_pdf
from ancientbook.text_reader import read_text_files


@dataclass(frozen=True)
class GenerateRequest:
    text_files: list[Path]
    output_path: Path
    font_path: Path | None = None
    title: str = "AncientBook"
    overwrite: bool = False


@dataclass(frozen=True)
class GenerateResult:
    output_path: Path
    page_count: int


def _validate_request(request: GenerateRequest) -> None:
    if not request.text_files:
        raise ValueError("Select at least one text file.")
    if request.output_path.suffix.lower() != ".pdf":
        raise ValueError("Output path must end with .pdf.")
    if request.font_path is not None and not request.font_path.exists():
        raise ValueError(f"Font file does not exist: {request.font_path}")


def generate_pdf_from_request(request: GenerateRequest) -> GenerateResult:
    _validate_request(request)
    text = read_text_files(request.text_files)
    tokens = parse_markup(text)
    settings = LayoutSettings()
    placements = layout_tokens(tokens, settings)
    write_pdf(
        request.output_path,
        placements,
        settings,
        request.font_path,
        request.title,
        overwrite=request.overwrite,
    )
    page_count = max((placement.page_index for placement in placements), default=0) + 1
    return GenerateResult(output_path=request.output_path, page_count=page_count)
