from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ancientbook.model import LayoutSettings


@dataclass(frozen=True)
class Choice:
    key: str
    label: str


TEMPLATE_CHOICES = (
    Choice("simple", "Simple paper"),
    Choice("classic", "Classic frame"),
    Choice("aged", "Light aged paper"),
)
PAPER_SIZE_CHOICES = (
    Choice("a4", "A4"),
    Choice("a5", "A5"),
)
FONT_SIZE_CHOICES = (
    Choice("small", "Small"),
    Choice("medium", "Medium"),
    Choice("large", "Large"),
)
COLUMN_DENSITY_CHOICES = (
    Choice("fewer", "Fewer"),
    Choice("standard", "Standard"),
    Choice("more", "More"),
)

DEFAULT_TEMPLATE = "simple"
DEFAULT_PAPER_SIZE = "a4"
DEFAULT_FONT_SIZE = "medium"
DEFAULT_COLUMNS = "standard"

_PAGE_SIZES = {
    "a4": (595, 842),
    "a5": (420, 595),
}
_FONT_SIZES = {
    "small": (16, 8),
    "medium": (18, 9),
    "large": (22, 11),
}
_COLUMNS = {
    "fewer": 10,
    "standard": 12,
    "more": 14,
}


def normalize_choice(value: str | None, choices: Sequence[Choice], default_key: str) -> str:
    valid = {choice.key for choice in choices}
    if default_key not in valid:
        raise ValueError(f"Invalid default choice: {default_key}")
    if value in valid:
        return str(value)
    return default_key


def choice_label(key: str, choices: Sequence[Choice]) -> str:
    for choice in choices:
        if choice.key == key:
            return choice.label
    return key


def build_layout_settings(
    paper_size: str = DEFAULT_PAPER_SIZE,
    font_size: str = DEFAULT_FONT_SIZE,
    columns: str = DEFAULT_COLUMNS,
) -> LayoutSettings:
    paper_key = normalize_choice(paper_size, PAPER_SIZE_CHOICES, DEFAULT_PAPER_SIZE)
    font_key = normalize_choice(font_size, FONT_SIZE_CHOICES, DEFAULT_FONT_SIZE)
    columns_key = normalize_choice(columns, COLUMN_DENSITY_CHOICES, DEFAULT_COLUMNS)

    page_width, page_height = _PAGE_SIZES[paper_key]
    body_size, comment_size = _FONT_SIZES[font_key]
    column_count = _COLUMNS[columns_key]

    default = LayoutSettings()
    row_count = default.rows
    if paper_key != DEFAULT_PAPER_SIZE or font_key != DEFAULT_FONT_SIZE:
        content_height = page_height - default.margin * 2
        row_count = max(8, content_height // max(body_size + 10, 1))

    return LayoutSettings(
        page_width=page_width,
        page_height=page_height,
        margin=default.margin,
        columns=column_count,
        rows=row_count,
        font_size=body_size,
        comment_font_size=comment_size,
    )
