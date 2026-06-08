from __future__ import annotations

from pathlib import Path


def default_output_path(text_files: list[Path], output_dir: Path | None) -> Path:
    directory = output_dir or _default_output_dir(text_files)
    if not text_files:
        return directory / "AncientBook.pdf"
    return directory / f"{text_files[0].stem}-AncientBook.pdf"


def unique_output_path(output_path: Path) -> Path:
    if not output_path.exists():
        return output_path

    for index in range(2, 10000):
        candidate = output_path.with_name(f"{output_path.stem}-{index}{output_path.suffix}")
        if not candidate.exists():
            return candidate

    raise ValueError("Could not find an unused output filename.")


def _default_output_dir(text_files: list[Path]) -> Path:
    if text_files:
        return text_files[0].parent
    return Path("")
