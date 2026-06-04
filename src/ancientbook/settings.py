from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from ancientbook.presets import (
    COLUMN_DENSITY_CHOICES,
    DEFAULT_COLUMNS,
    DEFAULT_FONT_SIZE,
    DEFAULT_PAPER_SIZE,
    DEFAULT_TEMPLATE,
    FONT_SIZE_CHOICES,
    PAPER_SIZE_CHOICES,
    TEMPLATE_CHOICES,
    normalize_choice,
)


@dataclass(frozen=True)
class AppSettings:
    last_text_dir: str = ""
    last_output_dir: str = ""
    last_font_path: str = ""
    template_key: str = DEFAULT_TEMPLATE
    paper_size: str = DEFAULT_PAPER_SIZE
    font_size: str = DEFAULT_FONT_SIZE
    columns: str = DEFAULT_COLUMNS


def default_settings_path() -> Path:
    return Path.home() / ".ancientbook" / "settings.json"


def load_settings(path: Path | None = None) -> AppSettings:
    settings_path = path or default_settings_path()
    if not settings_path.exists():
        return AppSettings()
    try:
        raw = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppSettings()
    if not isinstance(raw, dict):
        return AppSettings()
    return AppSettings(
        last_text_dir=str(raw.get("last_text_dir", "")),
        last_output_dir=str(raw.get("last_output_dir", "")),
        last_font_path=str(raw.get("last_font_path", "")),
        template_key=normalize_choice(raw.get("template_key"), TEMPLATE_CHOICES, DEFAULT_TEMPLATE),
        paper_size=normalize_choice(raw.get("paper_size"), PAPER_SIZE_CHOICES, DEFAULT_PAPER_SIZE),
        font_size=normalize_choice(raw.get("font_size"), FONT_SIZE_CHOICES, DEFAULT_FONT_SIZE),
        columns=normalize_choice(raw.get("columns"), COLUMN_DENSITY_CHOICES, DEFAULT_COLUMNS),
    )


def save_settings(path: Path | None, settings: AppSettings) -> None:
    settings_path = path or default_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
