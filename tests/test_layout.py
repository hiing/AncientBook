from ancientbook.model import LayoutSettings


def test_layout_settings_compute_capacity():
    settings = LayoutSettings(page_width=600, page_height=800, margin=60, columns=10, rows=20)

    assert settings.page_capacity == 200
    assert settings.column_width == 48
    assert settings.row_height == 34


from ancientbook.layout import layout_tokens
from ancientbook.model import Token, TokenKind


def test_layout_places_columns_right_to_left():
    settings = LayoutSettings(page_width=300, page_height=300, margin=50, columns=2, rows=2, font_size=16)
    tokens = [Token(TokenKind.TEXT, ch) for ch in "天地玄"]

    placements = layout_tokens(tokens, settings)

    assert [(p.text, p.page_index, p.column_index, p.row_index) for p in placements] == [
        ("天", 0, 0, 0),
        ("地", 0, 0, 1),
        ("玄", 0, 1, 0),
    ]
    assert placements[0].x > placements[2].x


def test_layout_column_break_moves_to_next_column():
    settings = LayoutSettings(page_width=300, page_height=300, margin=50, columns=2, rows=3, font_size=16)
    tokens = [
        Token(TokenKind.TEXT, "天"),
        Token(TokenKind.COLUMN_BREAK),
        Token(TokenKind.TEXT, "地"),
    ]

    placements = layout_tokens(tokens, settings)

    assert [(p.text, p.column_index, p.row_index) for p in placements] == [
        ("天", 0, 0),
        ("地", 1, 0),
    ]


def test_layout_page_break_moves_to_new_page():
    settings = LayoutSettings(page_width=300, page_height=300, margin=50, columns=2, rows=3, font_size=16)
    tokens = [
        Token(TokenKind.TEXT, "天"),
        Token(TokenKind.PAGE_BREAK),
        Token(TokenKind.TEXT, "地"),
    ]

    placements = layout_tokens(tokens, settings)

    assert [(p.text, p.page_index, p.column_index, p.row_index) for p in placements] == [
        ("天", 0, 0, 0),
        ("地", 1, 0, 0),
    ]


def test_layout_comment_uses_comment_font_size_and_does_not_advance_body_slot():
    settings = LayoutSettings(page_width=300, page_height=300, margin=50, columns=2, rows=3, font_size=16, comment_font_size=8)
    tokens = [
        Token(TokenKind.TEXT, "天"),
        Token(TokenKind.COMMENT, "注"),
        Token(TokenKind.TEXT, "地"),
    ]

    placements = layout_tokens(tokens, settings)

    assert [(p.text, p.is_comment, p.row_index, p.font_size) for p in placements] == [
        ("天", False, 0, 16),
        ("注", True, 0, 8),
        ("地", False, 1, 16),
    ]
