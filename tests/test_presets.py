import pytest

from ancientbook.model import LayoutSettings
from ancientbook.presets import (
    COLUMN_DENSITY_CHOICES,
    FONT_SIZE_CHOICES,
    PAPER_SIZE_CHOICES,
    TEMPLATE_CHOICES,
    build_layout_settings,
    normalize_choice,
)


def test_choice_catalogs_expose_plain_language_options():
    assert [choice.label for choice in TEMPLATE_CHOICES] == [
        "素雅书页",
        "朱栏格页",
        "旧藏纸页",
    ]
    assert [choice.label for choice in FONT_SIZE_CHOICES] == ["小字", "中字", "大字"]
    assert [choice.label for choice in COLUMN_DENSITY_CHOICES] == ["疏朗", "标准", "紧凑"]
    assert [choice.key for choice in PAPER_SIZE_CHOICES] == ["a4", "a5"]
    assert [choice.key for choice in FONT_SIZE_CHOICES] == ["small", "medium", "large"]
    assert [choice.key for choice in COLUMN_DENSITY_CHOICES] == ["fewer", "standard", "more"]


def test_build_layout_settings_default_matches_current_layout():
    settings = build_layout_settings()

    assert settings == LayoutSettings()


def test_build_layout_settings_maps_a5_large_fewer():
    settings = build_layout_settings(paper_size="a5", font_size="large", columns="fewer")

    assert settings.page_width == 420
    assert settings.page_height == 595
    assert settings.font_size == 22
    assert settings.comment_font_size == 11
    assert settings.columns == 10
    assert settings.rows >= 12


def test_build_layout_settings_maps_a4_small_more():
    settings = build_layout_settings(paper_size="a4", font_size="small", columns="more")

    assert settings.page_width == 595
    assert settings.page_height == 842
    assert settings.font_size == 16
    assert settings.comment_font_size == 8
    assert settings.columns == 14


def test_build_layout_settings_caps_dense_columns_to_keep_text_clear_of_rules():
    settings = build_layout_settings(paper_size="a5", font_size="large", columns="more")

    assert settings.column_width >= settings.font_size + 8
    assert settings.columns <= 10


def test_normalize_choice_falls_back_for_invalid_values():
    assert normalize_choice("missing", PAPER_SIZE_CHOICES, default_key="a4") == "a4"
    assert normalize_choice("", FONT_SIZE_CHOICES, default_key="medium") == "medium"
    assert normalize_choice(None, COLUMN_DENSITY_CHOICES, default_key="standard") == "standard"


def test_normalize_choice_rejects_unknown_default():
    with pytest.raises(ValueError):
        normalize_choice("a4", PAPER_SIZE_CHOICES, default_key="missing")
