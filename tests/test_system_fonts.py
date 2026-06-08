from pathlib import Path

from ancientbook.system_fonts import (
    CUSTOM_FONT_KEY,
    FontChoice,
    available_font_choices,
    default_font_choice,
    resolve_font_path,
)


def test_available_font_choices_include_discovered_system_fonts(tmp_path: Path):
    fonts_dir = tmp_path / "Fonts"
    fonts_dir.mkdir()
    yahei = fonts_dir / "msyh.ttc"
    simsun = fonts_dir / "simsun.ttc"
    yahei.write_bytes(b"font")
    simsun.write_bytes(b"font")

    choices = available_font_choices(fonts_dir)

    assert choices[:2] == [
        FontChoice("msyh", "微软雅黑 / Microsoft YaHei", yahei),
        FontChoice("simsun", "宋体 / SimSun", simsun),
    ]
    assert choices[-1] == FontChoice(CUSTOM_FONT_KEY, "手动选择字体文件 / Custom font file", None)


def test_default_font_choice_uses_first_available_system_font(tmp_path: Path):
    fonts_dir = tmp_path / "Fonts"
    fonts_dir.mkdir()
    simsun = fonts_dir / "simsun.ttc"
    simsun.write_bytes(b"font")

    assert default_font_choice(fonts_dir) == "simsun"


def test_default_font_choice_falls_back_to_custom_when_no_system_font(tmp_path: Path):
    assert default_font_choice(tmp_path) == CUSTOM_FONT_KEY


def test_resolve_font_path_uses_system_or_custom_font(tmp_path: Path):
    fonts_dir = tmp_path / "Fonts"
    fonts_dir.mkdir()
    simkai = fonts_dir / "simkai.ttf"
    custom = tmp_path / "custom.ttf"
    simkai.write_bytes(b"font")
    custom.write_bytes(b"font")

    assert resolve_font_path("simkai", custom, fonts_dir) == simkai
    assert resolve_font_path(CUSTOM_FONT_KEY, custom, fonts_dir) == custom
    assert resolve_font_path("missing", custom, fonts_dir) == custom
    assert resolve_font_path(CUSTOM_FONT_KEY, None, fonts_dir) is None
