from __future__ import annotations

from pathlib import Path
from typing import Iterable


class TextReadError(RuntimeError):
    pass


def _clean_control_characters(text: str) -> str:
    allowed = {"\n", "\r", "\t"}
    return "".join(ch for ch in text if ch in allowed or ord(ch) >= 32)


def read_text_files(paths: Iterable[Path]) -> str:
    chunks: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise TextReadError(f"Cannot read text file: {path}") from exc
        except UnicodeDecodeError as exc:
            raise TextReadError(f"Text file must be UTF-8: {path}") from exc
        chunks.append(_clean_control_characters(text).strip())
    return "\n".join(chunk for chunk in chunks if chunk)
