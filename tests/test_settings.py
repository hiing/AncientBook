from pathlib import Path

from ancientbook.settings import AppSettings, load_settings, save_settings


def test_save_and_load_settings_round_trip(tmp_path: Path):
    path = tmp_path / "settings.json"
    settings = AppSettings(
        last_text_dir=str(tmp_path / "texts"),
        last_output_dir=str(tmp_path / "out"),
        last_font_path=str(tmp_path / "font.ttf"),
    )

    save_settings(path, settings)

    assert load_settings(path) == settings


def test_load_settings_returns_defaults_when_missing(tmp_path: Path):
    assert load_settings(tmp_path / "missing.json") == AppSettings()


def test_load_settings_ignores_invalid_json(tmp_path: Path):
    path = tmp_path / "settings.json"
    path.write_text("{not json", encoding="utf-8")

    assert load_settings(path) == AppSettings()
