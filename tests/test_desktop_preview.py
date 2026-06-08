from ancientbook.desktop.preview import create_preview_image


def test_create_preview_image_returns_scaled_page():
    image = create_preview_image("classic", "a5", "large", "fewer", max_height=260)

    assert image.height <= 260
    assert image.width > 100
    assert image.mode == "RGB"


def test_create_preview_image_draws_ink_marks():
    image = create_preview_image("aged", "a5", "medium", "standard", max_height=260)
    dark_pixels = 0

    pixels = image.tobytes()
    for index in range(0, len(pixels), 3):
        red, green, blue = pixels[index], pixels[index + 1], pixels[index + 2]
        if red < 80 and green < 70 and blue < 60:
            dark_pixels += 1

    assert dark_pixels > 100
