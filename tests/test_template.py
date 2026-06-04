from ancientbook.model import LayoutSettings
from ancientbook.template import create_simple_background


def test_create_simple_background_matches_page_size():
    settings = LayoutSettings(page_width=300, page_height=400)

    image = create_simple_background(settings)

    assert image.size == (300, 400)
    assert image.mode == "RGB"
    assert image.getpixel((10, 10)) == (244, 236, 216)
