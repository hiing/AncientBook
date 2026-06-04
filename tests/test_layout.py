from ancientbook.model import LayoutSettings


def test_layout_settings_compute_capacity():
    settings = LayoutSettings(page_width=600, page_height=800, margin=60, columns=10, rows=20)

    assert settings.page_capacity == 200
    assert settings.column_width == 48
    assert settings.row_height == 34
