from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    last_text_dir: str = ""
    last_output_dir: str = ""
    last_font_path: str = ""


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
    )


def save_settings(path: Path | None, settings: AppSettings) -> None:
    settings_path = path or default_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
