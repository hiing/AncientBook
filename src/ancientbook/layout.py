from __future__ import annotations

from ancientbook.model import GlyphPlacement, LayoutSettings, Token, TokenKind


def _body_position(settings: LayoutSettings, column_index: int, row_index: int) -> tuple[float, float]:
    x = settings.page_width - settings.margin - (column_index + 0.5) * settings.column_width
    y = settings.page_height - settings.margin - (row_index + 0.75) * settings.row_height
    return x, y


def _comment_position(settings: LayoutSettings, column_index: int, row_index: int) -> tuple[float, float]:
    body_x, body_y = _body_position(settings, column_index, row_index)
    return body_x - settings.column_width * 0.25, body_y


def _advance(page: int, column: int, row: int, settings: LayoutSettings) -> tuple[int, int, int]:
    row += 1
    if row < settings.rows:
        return page, column, row
    row = 0
    column += 1
    if column < settings.columns:
        return page, column, row
    return page + 1, 0, 0


def _next_column(page: int, column: int, settings: LayoutSettings) -> tuple[int, int, int]:
    column += 1
    if column < settings.columns:
        return page, column, 0
    return page + 1, 0, 0


def layout_tokens(tokens: list[Token], settings: LayoutSettings) -> list[GlyphPlacement]:
    placements: list[GlyphPlacement] = []
    page = 0
    column = 0
    row = 0
    last_body_slot = (0, 0, 0)

    for token in tokens:
        if token.kind == TokenKind.PAGE_BREAK:
            page, column, row = page + 1, 0, 0
            last_body_slot = (page, column, row)
            continue
        if token.kind == TokenKind.COLUMN_BREAK:
            page, column, row = _next_column(page, column, settings)
            last_body_slot = (page, column, row)
            continue
        if token.kind == TokenKind.COMMENT:
            comment_page, comment_column, comment_row = last_body_slot
            for index, ch in enumerate(token.value):
                x, y = _comment_position(settings, comment_column, comment_row + index)
                placements.append(
                    GlyphPlacement(
                        page_index=comment_page,
                        column_index=comment_column,
                        row_index=comment_row + index,
                        x=x,
                        y=y,
                        text=ch,
                        font_size=settings.comment_font_size,
                        is_comment=True,
                    )
                )
            continue
        if token.kind in {TokenKind.TEXT, TokenKind.BLANK}:
            x, y = _body_position(settings, column, row)
            placements.append(
                GlyphPlacement(
                    page_index=page,
                    column_index=column,
                    row_index=row,
                    x=x,
                    y=y,
                    text=token.value,
                    font_size=settings.font_size,
                    is_comment=False,
                )
            )
            last_body_slot = (page, column, row)
            page, column, row = _advance(page, column, row, settings)
    return placements
