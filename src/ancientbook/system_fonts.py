from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


CUSTOM_FONT_KEY = "custom"


@dataclass(frozen=True)
class FontChoice:
    key: str
    label: str
    path: Path | None


WINDOWS_FONT_CANDIDATES = (
    ("msyh", "微软雅黑 / Microsoft YaHei", ("msyh.ttc", "msyh.ttf")),
    ("simsun", "宋体 / SimSun", ("simsun.ttc", "simsun.ttf")),
    ("simkai", "楷体 / KaiTi", ("simkai.ttf",)),
    ("simfang", "仿宋 / FangSong", ("simfang.ttf",)),
    ("simhei", "黑体 / SimHei", ("simhei.ttf",)),
)


def default_windows_fonts_dir() -> Path:
    return Path("C:/Windows/Fonts")


def available_font_choices(fonts_dir: Path | None = None) -> list[FontChoice]:
    root = fonts_dir or default_windows_fonts_dir()
    choices: list[FontChoice] = []
    for key, label, filenames in WINDOWS_FONT_CANDIDATES:
        path = _first_existing(root, filenames)
        if path is not None:
            choices.append(FontChoice(key, label, path))
    choices.append(FontChoice(CUSTOM_FONT_KEY, "手动选择字体文件 / Custom font file", None))
    return choices


def default_font_choice(fonts_dir: Path | None = None) -> str:
    for choice in available_font_choices(fonts_dir):
        if choice.path is not None:
            return choice.key
    return CUSTOM_FONT_KEY


def resolve_font_path(
    font_choice_key: str,
    custom_font_path: Path | None,
    fonts_dir: Path | None = None,
) -> Path | None:
    for choice in available_font_choices(fonts_dir):
        if choice.key == font_choice_key and choice.path is not None:
            return choice.path
    return custom_font_path


def _first_existing(root: Path, filenames: tuple[str, ...]) -> Path | None:
    for filename in filenames:
        path = root / filename
        if path.exists():
            return path
    return None
