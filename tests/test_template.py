from ancientbook.model import LayoutSettings
from ancientbook.template import (
    create_background,
    create_simple_background,
    template_labels,
    template_keys,
)


def test_create_simple_background_matches_page_size():
    settings = LayoutSettings(page_width=300, page_height=400)

    image = create_simple_background(settings)

    assert image.size == (300, 400)
    assert image.mode == "RGB"
    assert image.getpixel((10, 10)) == (244, 236, 216)


def test_template_catalog_contains_three_templates():
    assert template_keys() == ["simple", "classic", "aged"]
    assert template_labels() == ["Simple paper", "Classic frame", "Light aged paper"]


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
