# AncientBook Core PDF Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first visible AncientBook pipeline: read Chinese text, parse simple markers, calculate vertical layout, draw a basic ancient-book page background, and generate a searchable PDF from a local font.

**Architecture:** Start with a testable Python core before adding the desktop interface. The core is split into small modules for text loading, marker parsing, layout calculation, background generation, and PDF writing, with a simple CLI used only as a development bridge until the PySide6 app is built.

**Tech Stack:** Python 3.11+, pytest, Pillow, ReportLab, pypdf for PDF verification, PySide6 deferred to the next plan.

---

## Scope

This plan implements the first working slice from the design spec. It does not implement the desktop UI, settings persistence, PyInstaller packaging, or multi-template UI. Those belong in follow-up plans after the PDF pipeline is proven.

This plan creates:

- A Python package named `ancientbook`.
- A CLI command for development use.
- Unit tests for text reading, marker parsing, and layout.
- Integration tests for generating a PDF.
- One simple built-in background template.
- A short user-facing README section that explains the first test run.

## File Structure

- `pyproject.toml`: project metadata, dependencies, pytest configuration, and CLI entry point.
- `README.md`: current project status and safe first-run instructions.
- `src/ancientbook/__init__.py`: package version.
- `src/ancientbook/model.py`: shared dataclasses and layout settings.
- `src/ancientbook/text_reader.py`: safe UTF-8 text loading and control-character filtering.
- `src/ancientbook/markup.py`: parser for `【...】`, `%`, `$`, `@`, and basic punctuation handling.
- `src/ancientbook/layout.py`: vertical layout engine.
- `src/ancientbook/template.py`: Pillow background generation.
- `src/ancientbook/pdf.py`: ReportLab PDF writer.
- `src/ancientbook/cli.py`: development CLI for producing a PDF without the desktop UI.
- `tests/test_text_reader.py`: text reader tests.
- `tests/test_markup.py`: parser tests.
- `tests/test_layout.py`: layout tests.
- `tests/test_pdf_pipeline.py`: PDF generation integration tests.
- `examples/sample.txt`: small Chinese sample input.

## Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/ancientbook/__init__.py`
- Create: `tests/test_package.py`

- [ ] **Step 1: Write the package import test**

Create `tests/test_package.py`:

```python
from ancientbook import __version__


def test_package_exposes_version():
    assert __version__ == "0.1.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_package.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook'
```

- [ ] **Step 3: Create project metadata**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ancientbook"
version = "0.1.0"
description = "Chinese ancient-book-style vertical PDF generator"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "Pillow>=10.4",
  "reportlab>=4.2",
  "pypdf>=4.2",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2",
]

[project.scripts]
ancientbook = "ancientbook.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 4: Create package file**

Create `src/ancientbook/__init__.py`:

```python
__version__ = "0.1.0"
```

- [ ] **Step 5: Create initial README**

Create `README.md`:

```markdown
# AncientBook

AncientBook is a clean-room Python desktop-tool project for generating Chinese ancient-book-style vertical PDFs from plain text.

Current status: core PDF pipeline planning and implementation.

Safety principles:

- User text stays local.
- User text is treated as data, never as code.
- Fonts are selected by the user and are not bundled unless their licenses allow redistribution.
- The project does not copy vRain source code.
```

- [ ] **Step 6: Run test to verify it passes**

Run:

```powershell
python -m pytest tests/test_package.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 7: Commit**

Run:

```powershell
git add pyproject.toml README.md src tests
git commit -m "chore: add Python project skeleton"
```

## Task 2: Shared Data Model

**Files:**
- Create: `src/ancientbook/model.py`
- Create: `tests/test_layout.py`

- [ ] **Step 1: Write model defaults test**

Create `tests/test_layout.py`:

```python
from ancientbook.model import LayoutSettings


def test_layout_settings_compute_capacity():
    settings = LayoutSettings(page_width=600, page_height=800, margin=60, columns=10, rows=20)

    assert settings.page_capacity == 200
    assert settings.column_width == 48
    assert settings.row_height == 34
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_layout.py::test_layout_settings_compute_capacity -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.model'
```

- [ ] **Step 3: Implement shared model**

Create `src/ancientbook/model.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
python -m pytest tests/test_layout.py::test_layout_settings_compute_capacity -v
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/model.py tests/test_layout.py
git commit -m "feat: add shared layout model"
```

## Task 3: Safe Text Reader

**Files:**
- Create: `src/ancientbook/text_reader.py`
- Create: `tests/test_text_reader.py`

- [ ] **Step 1: Write text reader tests**

Create `tests/test_text_reader.py`:

```python
from pathlib import Path

import pytest

from ancientbook.text_reader import TextReadError, read_text_files


def test_read_text_files_merges_utf8_files(tmp_path: Path):
    first = tmp_path / "001.txt"
    second = tmp_path / "002.txt"
    first.write_text("天地玄黃", encoding="utf-8")
    second.write_text("宇宙洪荒", encoding="utf-8")

    assert read_text_files([first, second]) == "天地玄黃\n宇宙洪荒"


def test_read_text_files_removes_unsupported_control_characters(tmp_path: Path):
    source = tmp_path / "book.txt"
    source.write_text("天\u0000地\t玄\n黃", encoding="utf-8")

    assert read_text_files([source]) == "天地\t玄\n黃"


def test_read_text_files_reports_missing_file(tmp_path: Path):
    missing = tmp_path / "missing.txt"

    with pytest.raises(TextReadError) as exc:
        read_text_files([missing])

    assert "Cannot read text file" in str(exc.value)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_text_reader.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.text_reader'
```

- [ ] **Step 3: Implement safe text reader**

Create `src/ancientbook/text_reader.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Iterable


class TextReadError(RuntimeError):
    pass


def _clean_control_characters(text: str) -> str:
    allowed = {"\n", "\r", "\t"}
    return "".join(ch for ch in text if ch in allowed or ord(ch) >= 32)


def read_text_files(paths: Iterable[Path]) -> str:
    chunks: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise TextReadError(f"Cannot read text file: {path}") from exc
        except UnicodeDecodeError as exc:
            raise TextReadError(f"Text file must be UTF-8: {path}") from exc
        chunks.append(_clean_control_characters(text).strip())
    return "\n".join(chunk for chunk in chunks if chunk)
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```powershell
python -m pytest tests/test_text_reader.py -v
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/text_reader.py tests/test_text_reader.py
git commit -m "feat: add safe text reader"
```

## Task 4: Markup Parser

**Files:**
- Create: `src/ancientbook/markup.py`
- Create: `tests/test_markup.py`

- [ ] **Step 1: Write parser tests**

Create `tests/test_markup.py`:

```python
from ancientbook.markup import parse_markup
from ancientbook.model import TokenKind


def kinds_and_values(text: str):
    return [(token.kind, token.value) for token in parse_markup(text)]


def test_parse_text_comment_and_blank():
    assert kinds_and_values("天地【注】@玄") == [
        (TokenKind.TEXT, "天"),
        (TokenKind.TEXT, "地"),
        (TokenKind.COMMENT, "注"),
        (TokenKind.BLANK, " "),
        (TokenKind.TEXT, "玄"),
    ]


def test_parse_page_and_column_breaks():
    assert kinds_and_values("天%地$玄") == [
        (TokenKind.TEXT, "天"),
        (TokenKind.PAGE_BREAK, ""),
        (TokenKind.TEXT, "地"),
        (TokenKind.COLUMN_BREAK, ""),
        (TokenKind.TEXT, "玄"),
    ]


def test_unclosed_comment_is_preserved_as_text():
    assert kinds_and_values("天地【未完") == [
        (TokenKind.TEXT, "天"),
        (TokenKind.TEXT, "地"),
        (TokenKind.TEXT, "【"),
        (TokenKind.TEXT, "未"),
        (TokenKind.TEXT, "完"),
    ]


def test_normalize_punctuation_to_period():
    assert kinds_and_values("天，地！") == [
        (TokenKind.TEXT, "天"),
        (TokenKind.TEXT, "。"),
        (TokenKind.TEXT, "地"),
        (TokenKind.TEXT, "。"),
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_markup.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.markup'
```

- [ ] **Step 3: Implement parser**

Create `src/ancientbook/markup.py`:

```python
from __future__ import annotations

from ancientbook.model import Token, TokenKind


PUNCTUATION_TO_PERIOD = {
    "，",
    "、",
    "；",
    "：",
    "！",
    "？",
    ",",
    ";",
    ":",
    "!",
    "?",
}


def _normalize_char(ch: str) -> str:
    if ch in PUNCTUATION_TO_PERIOD:
        return "。"
    return ch


def parse_markup(text: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "【":
            end = text.find("】", i + 1)
            if end == -1:
                tokens.append(Token(TokenKind.TEXT, ch))
                i += 1
                continue
            tokens.append(Token(TokenKind.COMMENT, text[i + 1 : end]))
            i = end + 1
            continue
        if ch == "%":
            tokens.append(Token(TokenKind.PAGE_BREAK))
            i += 1
            continue
        if ch == "$":
            tokens.append(Token(TokenKind.COLUMN_BREAK))
            i += 1
            continue
        if ch == "@":
            tokens.append(Token(TokenKind.BLANK, " "))
            i += 1
            continue
        if ch in {"\r", "\n", "\t"}:
            i += 1
            continue
        tokens.append(Token(TokenKind.TEXT, _normalize_char(ch)))
        i += 1
    return tokens
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```powershell
python -m pytest tests/test_markup.py -v
```

Expected:

```text
4 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/markup.py tests/test_markup.py
git commit -m "feat: parse simple ancient-book markup"
```

## Task 5: Vertical Layout Engine

**Files:**
- Create: `src/ancientbook/layout.py`
- Modify: `tests/test_layout.py`

- [ ] **Step 1: Add layout engine tests**

Append to `tests/test_layout.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_layout.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.layout'
```

- [ ] **Step 3: Implement layout engine**

Create `src/ancientbook/layout.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```powershell
python -m pytest tests/test_layout.py -v
```

Expected:

```text
5 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/layout.py tests/test_layout.py
git commit -m "feat: calculate vertical text layout"
```

## Task 6: Background Template

**Files:**
- Create: `src/ancientbook/template.py`
- Create: `tests/test_template.py`

- [ ] **Step 1: Write template test**

Create `tests/test_template.py`:

```python
from ancientbook.model import LayoutSettings
from ancientbook.template import create_simple_background


def test_create_simple_background_matches_page_size():
    settings = LayoutSettings(page_width=300, page_height=400)

    image = create_simple_background(settings)

    assert image.size == (300, 400)
    assert image.mode == "RGB"
    assert image.getpixel((10, 10)) == (244, 236, 216)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_template.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.template'
```

- [ ] **Step 3: Implement simple background**

Create `src/ancientbook/template.py`:

```python
from __future__ import annotations

from PIL import Image, ImageDraw

from ancientbook.model import LayoutSettings


PAPER_COLOR = (244, 236, 216)
LINE_COLOR = (86, 58, 38)


def create_simple_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), PAPER_COLOR)
    draw = ImageDraw.Draw(image)

    left = settings.margin // 2
    top = settings.margin // 2
    right = settings.page_width - settings.margin // 2
    bottom = settings.page_height - settings.margin // 2

    draw.rectangle((left, top, right, bottom), outline=LINE_COLOR, width=2)
    draw.rectangle(
        (settings.margin, settings.margin, settings.page_width - settings.margin, settings.page_height - settings.margin),
        outline=LINE_COLOR,
        width=1,
    )

    center_x = settings.page_width // 2
    draw.line((center_x, top, center_x, bottom), fill=LINE_COLOR, width=1)
    return image
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
python -m pytest tests/test_template.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/template.py tests/test_template.py
git commit -m "feat: draw simple page background"
```

## Task 7: PDF Generator

**Files:**
- Create: `src/ancientbook/pdf.py`
- Create: `tests/test_pdf_pipeline.py`

- [ ] **Step 1: Write PDF generation test**

Create `tests/test_pdf_pipeline.py`:

```python
from pathlib import Path

from pypdf import PdfReader

from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.model import LayoutSettings
from ancientbook.pdf import PdfGenerationError, write_pdf


def test_write_pdf_creates_readable_pdf(tmp_path: Path):
    output = tmp_path / "book.pdf"
    settings = LayoutSettings(page_width=300, page_height=400, margin=40, columns=4, rows=6, font_size=14)
    tokens = parse_markup("天地玄黃")
    placements = layout_tokens(tokens, settings)

    write_pdf(output, placements, settings, font_path=None, title="Test Book")

    reader = PdfReader(str(output))
    assert len(reader.pages) == 1
    assert output.stat().st_size > 1000


def test_write_pdf_refuses_to_overwrite_without_flag(tmp_path: Path):
    output = tmp_path / "book.pdf"
    output.write_bytes(b"existing")
    settings = LayoutSettings(page_width=300, page_height=400)

    try:
        write_pdf(output, [], settings, font_path=None, title="Test Book")
    except PdfGenerationError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("Expected PdfGenerationError")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_pdf_pipeline.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.pdf'
```

- [ ] **Step 3: Implement PDF generator**

Create `src/ancientbook/pdf.py`:

```python
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from ancientbook.model import GlyphPlacement, LayoutSettings
from ancientbook.template import create_simple_background


class PdfGenerationError(RuntimeError):
    pass


def _register_font(font_path: Path | None) -> str:
    if font_path is None:
        return "Helvetica"
    path = Path(font_path)
    if not path.exists():
        raise PdfGenerationError(f"Font file does not exist: {path}")
    font_name = f"AncientBookFont-{abs(hash(path))}"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(path)))
    return font_name


def _background_reader(settings: LayoutSettings) -> ImageReader:
    image = create_simple_background(settings)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer)


def write_pdf(
    output_path: Path,
    placements: list[GlyphPlacement],
    settings: LayoutSettings,
    font_path: Path | None,
    title: str,
    overwrite: bool = False,
) -> None:
    output = Path(output_path)
    if output.exists() and not overwrite:
        raise PdfGenerationError(f"Output PDF already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    font_name = _register_font(font_path)
    page_count = max((placement.page_index for placement in placements), default=0) + 1
    pdf = canvas.Canvas(str(output), pagesize=(settings.page_width, settings.page_height))
    pdf.setTitle(title)
    pdf.setAuthor("")
    pdf.setCreator("AncientBook")

    background = _background_reader(settings)
    for page_index in range(page_count):
        pdf.drawImage(background, 0, 0, width=settings.page_width, height=settings.page_height)
        for placement in placements:
            if placement.page_index != page_index:
                continue
            pdf.setFont(font_name, placement.font_size)
            pdf.drawString(placement.x, placement.y, placement.text)
        pdf.showPage()
    pdf.save()
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```powershell
python -m pytest tests/test_pdf_pipeline.py -v
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/pdf.py tests/test_pdf_pipeline.py
git commit -m "feat: generate basic vertical PDF"
```

## Task 8: Development CLI And Example

**Files:**
- Create: `src/ancientbook/cli.py`
- Create: `examples/sample.txt`
- Modify: `README.md`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write CLI test**

Create `tests/test_cli.py`:

```python
from pathlib import Path

from ancientbook.cli import main


def test_cli_generates_pdf(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    exit_code = main([str(source), "--output", str(output), "--overwrite"])

    assert exit_code == 0
    assert output.exists()
    assert output.stat().st_size > 1000
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_cli.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.cli'
```

- [ ] **Step 3: Implement CLI**

Create `src/ancientbook/cli.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.model import LayoutSettings
from ancientbook.pdf import PdfGenerationError, write_pdf
from ancientbook.text_reader import TextReadError, read_text_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an ancient-book-style vertical PDF.")
    parser.add_argument("text_files", nargs="+", help="UTF-8 .txt files to render")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--font", default=None, help="Optional local .ttf or .otf font path")
    parser.add_argument("--title", default="AncientBook", help="PDF title")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output PDF if it exists")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = read_text_files([Path(path) for path in args.text_files])
        tokens = parse_markup(text)
        settings = LayoutSettings()
        placements = layout_tokens(tokens, settings)
        font_path = Path(args.font) if args.font else None
        write_pdf(Path(args.output), placements, settings, font_path, args.title, overwrite=args.overwrite)
    except (TextReadError, PdfGenerationError) as exc:
        parser.exit(2, f"AncientBook error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Create example text**

Create `examples/sample.txt`:

```text
天地玄黃，宇宙洪荒。
日月盈昃，辰宿列張。
寒來暑往，秋收冬藏。
閏餘成歲，律呂調陽。
```

- [ ] **Step 5: Update README with first-run command**

Append to `README.md`:

````markdown

## Development First Run

Install the project in editable mode:

```powershell
python -m pip install -e ".[dev]"
```

Generate a sample PDF:

```powershell
ancientbook examples/sample.txt --output output/sample.pdf --overwrite
```

Use `--font C:\Path\To\YourFont.ttf` to render Chinese characters with a local font. Fonts are not bundled by default because font redistribution rights vary.
````

- [ ] **Step 6: Run CLI test**

Run:

```powershell
python -m pytest tests/test_cli.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 7: Run full test suite**

Run:

```powershell
python -m pytest -v
```

Expected:

```text
All tests pass
```

- [ ] **Step 8: Commit**

Run:

```powershell
git add src/ancientbook/cli.py examples/sample.txt README.md tests/test_cli.py
git commit -m "feat: add development PDF CLI"
```

## Task 9: Verification And Next-Plan Notes

**Files:**
- Modify: `README.md`
- Create: `docs/superpowers/plans/2026-06-04-ancientbook-next-ui-plan-notes.md`

- [ ] **Step 1: Run full verification**

Run:

```powershell
python -m pytest -v
```

Expected:

```text
All tests pass
```

- [ ] **Step 2: Generate manual sample PDF**

Run:

```powershell
python -m ancientbook.cli examples/sample.txt --output output/sample.pdf --overwrite
```

Expected:

```text
No terminal error, and output/sample.pdf exists.
```

- [ ] **Step 3: Add README status note**

Append to `README.md`:

```markdown

## Implemented Core Slice

The first core slice can:

- Read UTF-8 text files.
- Parse `【comment】`, `%`, `$`, and `@`.
- Lay out text vertically from right to left.
- Draw a simple ancient-book-style page background.
- Generate a PDF locally.

The desktop interface, user settings, richer templates, and Windows packaging are planned next.
```

- [ ] **Step 4: Create next-plan notes**

Create `docs/superpowers/plans/2026-06-04-ancientbook-next-ui-plan-notes.md`:

```markdown
# AncientBook Next UI Plan Notes

The next plan should build the PySide6 desktop interface on top of the tested core pipeline.

Recommended next tasks:

1. Add an application service function that accepts input paths, output path, optional font path, title, and overwrite flag.
2. Add a PySide6 main window with file pickers and a Generate button.
3. Run PDF generation in a worker thread so the UI stays responsive.
4. Show friendly errors for unreadable text files, missing fonts, and existing output files.
5. Save last-used paths in JSON settings.
6. Add a basic Windows packaging plan with PyInstaller.
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add README.md docs/superpowers/plans/2026-06-04-ancientbook-next-ui-plan-notes.md
git commit -m "docs: record core verification and UI follow-up"
```

Do not commit `output/sample.pdf`; it is a generated verification artifact.

## Self-Review Notes

Spec coverage:

- Text reader: covered by Task 3.
- Marker parsing: covered by Task 4.
- Right-to-left vertical layout: covered by Task 5.
- Basic background template: covered by Task 6.
- Searchable PDF path: covered by Task 7, with the caveat that Chinese rendering needs a user-selected local font.
- Clear overwrite safety: covered by Task 7.
- Development visibility: covered by Task 8 and Task 9.
- Desktop UI, settings, packaging, and multiple templates are intentionally left for follow-up plans because this plan targets the first core slice.

Red-flag scan:

- No unresolved placeholder instructions remain.

Type consistency:

- `LayoutSettings`, `Token`, `TokenKind`, and `GlyphPlacement` names are consistent across tasks.
- CLI calls the same pipeline defined by earlier tasks.
