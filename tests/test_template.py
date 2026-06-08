from ancientbook.model import LayoutSettings
from ancientbook.template import (
    _corner_decoration_box,
    create_aged_background,
    create_background,
    create_classic_background,
    create_simple_background,
    template_labels,
    template_keys,
)


def test_create_simple_background_matches_page_size():
    settings = LayoutSettings(page_width=300, page_height=400)

    image = create_simple_background(settings)

    assert image.size == (300, 400)
    assert image.mode == "RGB"
    red, green, blue = image.getpixel((10, 10))
    assert red > green > blue
    assert 210 <= blue <= 230


def test_template_catalog_contains_three_templates():
    assert template_keys() == ["simple", "classic", "aged"]
    assert template_labels() == ["素雅书页", "朱栏格页", "旧藏纸页"]


def test_create_background_supports_each_template():
    settings = LayoutSettings(page_width=320, page_height=480)

    images = [create_background(key, settings) for key in template_keys()]

    assert all(image.size == (320, 480) for image in images)
    assert len({image.tobytes() for image in images}) == 3


def test_create_background_falls_back_to_simple_for_unknown_template():
    settings = LayoutSettings(page_width=320, page_height=480)

    simple = create_background("simple", settings)
    fallback = create_background("missing", settings)

    assert fallback.tobytes() == simple.tobytes()


def test_classic_background_uses_vermilion_ruling():
    settings = LayoutSettings(page_width=320, page_height=480)

    image = create_classic_background(settings)
    colors = image.getcolors(maxcolors=100000)

    assert colors is not None
    assert any(red > 130 and green < 80 and blue < 70 for _count, (red, green, blue) in colors)


def test_corner_decoration_stays_outside_text_content_area():
    settings = LayoutSettings(page_width=420, page_height=595, margin=56, columns=10, rows=15, font_size=22)

    left, top, right, bottom = _corner_decoration_box(settings)

    assert left < settings.margin
    assert top < settings.margin
    assert right > settings.page_width - settings.margin
    assert bottom > settings.page_height - settings.margin


def test_aged_background_has_rich_paper_texture():
    settings = LayoutSettings(page_width=320, page_height=480)

    image = create_aged_background(settings)
    colors = image.getcolors(maxcolors=100000)

    assert colors is not None
    assert len(colors) >= 24
