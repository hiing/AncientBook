from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenKind(str, Enum):
    TEXT = "text"
    COMMENT = "comment"
    PAGE_BREAK = "page_break"
    COLUMN_BREAK = "column_break"
    BLANK = "blank"


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str = ""


@dataclass(frozen=True)
class LayoutSettings:
    page_width: int = 595
    page_height: int = 842
    margin: int = 56
    columns: int = 12
    rows: int = 24
    font_size: int = 18
    comment_font_size: int = 9

    @property
    def page_capacity(self) -> int:
        return self.columns * self.rows

    @property
    def content_width(self) -> int:
        return self.page_width - self.margin * 2

    @property
    def content_height(self) -> int:
        return self.page_height - self.margin * 2

    @property
    def column_width(self) -> int:
        return self.content_width // self.columns

    @property
    def row_height(self) -> int:
        return self.content_height // self.rows


@dataclass(frozen=True)
class GlyphPlacement:
    page_index: int
    column_index: int
    row_index: int
    x: float
    y: float
    text: str
    font_size: int
    is_comment: bool = False
