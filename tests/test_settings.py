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


def test_save_and_load_settings_with_usability_choices(tmp_path: Path):
    path = tmp_path / "settings.json"
    settings = AppSettings(
        last_text_dir=str(tmp_path / "texts"),
        last_output_dir=str(tmp_path / "out"),
        last_font_path=str(tmp_path / "font.ttf"),
        template_key="aged",
        paper_size="a5",
        font_size="large",
        columns="fewer",
    )

    save_settings(path, settings)

    assert load_settings(path) == settings


def test_load_settings_falls_back_for_invalid_choice_values(tmp_path: Path):
    path = tmp_path / "settings.json"
    path.write_text(
        '{"template_key":"bad","paper_size":"bad","font_size":"bad","columns":"bad"}',
        encoding="utf-8",
    )

    settings = load_settings(path)

    assert settings.template_key == "simple"
    assert settings.paper_size == "a4"
    assert settings.font_size == "medium"
    assert settings.columns == "standard"
