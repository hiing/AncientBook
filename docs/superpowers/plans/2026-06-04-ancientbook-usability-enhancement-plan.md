# AncientBook Usability Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add plain-language template and layout choices, preflight checks, friendly errors, and settings persistence to make the desktop app easier for non-programmers.

**Architecture:** Add a small preset layer that maps UI/CLI choices to `LayoutSettings`, then thread those choices through app service, CLI, PDF generation, settings, and desktop UI. Keep template rendering in `template.py`, keep validation in `app_service.py`, and avoid adding preview or bundled assets in this slice.

**Tech Stack:** Python 3.11+, PySide6, Pillow, ReportLab, pytest, PyInstaller.

---

## File Structure

- `src/ancientbook/presets.py`: new module for safe choice constants and `LayoutSettings` mapping.
- `src/ancientbook/template.py`: add named template catalog and three procedural backgrounds.
- `src/ancientbook/pdf.py`: accept a template key when drawing backgrounds.
- `src/ancientbook/app_service.py`: extend `GenerateRequest`, add preflight checks, friendly error class, and preset integration.
- `src/ancientbook/cli.py`: add optional preset flags and route through `GenerateRequest`.
- `src/ancientbook/settings.py`: persist template, paper size, font size, and column density.
- `src/ancientbook/desktop/main_window.py`: add combo boxes, save choices, preflight no-font warning, and friendly error display.
- `src/ancientbook/desktop/worker.py`: pass friendly messages from service errors.
- `README.md`: update user-facing instructions for new choices.
- `docs/release-checklists/non-programmer-acceptance.md`: add manual checks for templates and layouts.
- `tests/test_presets.py`: new tests for preset mappings.
- `tests/test_template.py`: extend tests for template catalog.
- `tests/test_pdf_pipeline.py`: extend tests for template-aware PDF generation.
- `tests/test_app_service.py`: extend tests for friendly preflight validation and preset usage.
- `tests/test_cli.py`: extend tests for CLI preset flags.
- `tests/test_settings.py`: extend tests for persisted choices and invalid fallback.
- `tests/test_desktop_imports.py`: existing import smoke tests should continue to pass.

## Task 1: Add Layout Presets

**Files:**
- Create: `src/ancientbook/presets.py`
- Create: `tests/test_presets.py`

- [ ] **Step 1: Write failing preset tests**

Create `tests/test_presets.py`:

```python
import pytest

from ancientbook.model import LayoutSettings
from ancientbook.presets import (
    COLUMN_DENSITY_CHOICES,
    FONT_SIZE_CHOICES,
    PAPER_SIZE_CHOICES,
    TEMPLATE_CHOICES,
    build_layout_settings,
    normalize_choice,
)


def test_choice_catalogs_expose_plain_language_options():
    assert [choice.label for choice in TEMPLATE_CHOICES] == [
        "Simple paper",
        "Classic frame",
        "Light aged paper",
    ]
    assert [choice.key for choice in PAPER_SIZE_CHOICES] == ["a4", "a5"]
    assert [choice.key for choice in FONT_SIZE_CHOICES] == ["small", "medium", "large"]
    assert [choice.key for choice in COLUMN_DENSITY_CHOICES] == ["fewer", "standard", "more"]


def test_build_layout_settings_default_matches_current_layout():
    settings = build_layout_settings()

    assert settings == LayoutSettings()


def test_build_layout_settings_maps_a5_large_fewer():
    settings = build_layout_settings(paper_size="a5", font_size="large", columns="fewer")

    assert settings.page_width == 420
    assert settings.page_height == 595
    assert settings.font_size == 22
    assert settings.comment_font_size == 11
    assert settings.columns == 10
    assert settings.rows >= 12


def test_build_layout_settings_maps_a4_small_more():
    settings = build_layout_settings(paper_size="a4", font_size="small", columns="more")

    assert settings.page_width == 595
    assert settings.page_height == 842
    assert settings.font_size == 16
    assert settings.comment_font_size == 8
    assert settings.columns == 14


def test_normalize_choice_falls_back_for_invalid_values():
    assert normalize_choice("missing", PAPER_SIZE_CHOICES, default_key="a4") == "a4"
    assert normalize_choice("", FONT_SIZE_CHOICES, default_key="medium") == "medium"
    assert normalize_choice(None, COLUMN_DENSITY_CHOICES, default_key="standard") == "standard"


def test_normalize_choice_rejects_unknown_default():
    with pytest.raises(ValueError):
        normalize_choice("a4", PAPER_SIZE_CHOICES, default_key="missing")
```

- [ ] **Step 2: Run preset tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_presets.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.presets'
```

- [ ] **Step 3: Implement presets module**

Create `src/ancientbook/presets.py`:

```python
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
```

- [ ] **Step 4: Run preset tests to verify they pass**

Run:

```powershell
python -m pytest tests/test_presets.py -v
```

Expected:

```text
6 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/presets.py tests/test_presets.py
git commit -m "feat: add layout preset choices"
```

## Task 2: Add Named Background Templates

**Files:**
- Modify: `src/ancientbook/template.py`
- Modify: `src/ancientbook/pdf.py`
- Modify: `tests/test_template.py`
- Modify: `tests/test_pdf_pipeline.py`

- [ ] **Step 1: Write failing template catalog tests**

Replace `tests/test_template.py` with:

```python
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
```

- [ ] **Step 2: Write failing PDF template test**

Append to `tests/test_pdf_pipeline.py`:

```python
def test_write_pdf_accepts_named_template(tmp_path: Path):
    output = tmp_path / "book-aged.pdf"
    settings = LayoutSettings(page_width=300, page_height=400, margin=40, columns=4, rows=6, font_size=14)
    tokens = parse_markup("天地玄黃")
    placements = layout_tokens(tokens, settings)

    write_pdf(output, placements, settings, font_path=None, title="Test Book", template_key="aged")

    reader = PdfReader(str(output))
    assert len(reader.pages) == 1
    assert output.stat().st_size > 1000
```

- [ ] **Step 3: Run template tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_template.py tests/test_pdf_pipeline.py::test_write_pdf_accepts_named_template -v
```

Expected:

```text
ImportError or TypeError
```

- [ ] **Step 4: Implement template catalog**

Update `src/ancientbook/template.py`:

```python
from __future__ import annotations

from collections.abc import Callable

from PIL import Image, ImageDraw

from ancientbook.model import LayoutSettings
from ancientbook.presets import TEMPLATE_CHOICES


PAPER_COLOR = (244, 236, 216)
AGED_PAPER_COLOR = (238, 226, 198)
LINE_COLOR = (86, 58, 38)
LIGHT_LINE_COLOR = (136, 102, 74)


def _draw_basic_frame(image: Image.Image, settings: LayoutSettings, line_color: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(image)
    left = settings.margin // 2
    top = settings.margin // 2
    right = settings.page_width - settings.margin // 2
    bottom = settings.page_height - settings.margin // 2

    draw.rectangle((left, top, right, bottom), outline=line_color, width=2)
    draw.rectangle(
        (settings.margin, settings.margin, settings.page_width - settings.margin, settings.page_height - settings.margin),
        outline=line_color,
        width=1,
    )

    center_x = settings.page_width // 2
    draw.line((center_x, top, center_x, bottom), fill=line_color, width=1)


def create_simple_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), PAPER_COLOR)
    _draw_basic_frame(image, settings, LINE_COLOR)
    return image


def create_classic_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), PAPER_COLOR)
    draw = ImageDraw.Draw(image)
    _draw_basic_frame(image, settings, LINE_COLOR)
    inset = settings.margin + 12
    draw.rectangle(
        (inset, inset, settings.page_width - inset, settings.page_height - inset),
        outline=LINE_COLOR,
        width=1,
    )
    return image


def create_aged_background(settings: LayoutSettings) -> Image.Image:
    image = Image.new("RGB", (settings.page_width, settings.page_height), AGED_PAPER_COLOR)
    draw = ImageDraw.Draw(image)
    for y in range(0, settings.page_height, 18):
        tone = (232, 217, 188) if y % 36 == 0 else (242, 231, 205)
        draw.line((0, y, settings.page_width, y), fill=tone, width=1)
    _draw_basic_frame(image, settings, LIGHT_LINE_COLOR)
    return image


_TEMPLATE_BUILDERS: dict[str, Callable[[LayoutSettings], Image.Image]] = {
    "simple": create_simple_background,
    "classic": create_classic_background,
    "aged": create_aged_background,
}


def template_keys() -> list[str]:
    return [choice.key for choice in TEMPLATE_CHOICES]


def template_labels() -> list[str]:
    return [choice.label for choice in TEMPLATE_CHOICES]


def create_background(template_key: str, settings: LayoutSettings) -> Image.Image:
    builder = _TEMPLATE_BUILDERS.get(template_key, create_simple_background)
    return builder(settings)
```

- [ ] **Step 5: Update PDF generator to accept template key**

Update `src/ancientbook/pdf.py`:

```python
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from ancientbook.model import GlyphPlacement, LayoutSettings
from ancientbook.presets import DEFAULT_TEMPLATE
from ancientbook.template import create_background


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


def _background_reader(settings: LayoutSettings, template_key: str) -> ImageReader:
    image = create_background(template_key, settings)
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
    template_key: str = DEFAULT_TEMPLATE,
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

    background = _background_reader(settings, template_key)
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

- [ ] **Step 6: Run template and PDF tests**

Run:

```powershell
python -m pytest tests/test_template.py tests/test_pdf_pipeline.py -v
```

Expected:

```text
All selected tests pass
```

- [ ] **Step 7: Commit**

Run:

```powershell
git add src/ancientbook/template.py src/ancientbook/pdf.py tests/test_template.py tests/test_pdf_pipeline.py
git commit -m "feat: add procedural background templates"
```

## Task 3: Add Service Preflight And CLI Flags

**Files:**
- Modify: `src/ancientbook/app_service.py`
- Modify: `src/ancientbook/cli.py`
- Modify: `tests/test_app_service.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing app service tests**

Append to `tests/test_app_service.py`:

```python
from pypdf import PdfReader

from ancientbook.app_service import FriendlyGenerationError


def test_generate_pdf_from_request_rejects_missing_text_file_with_friendly_message(tmp_path: Path):
    output = tmp_path / "sample.pdf"
    missing = tmp_path / "missing.txt"

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[missing], output_path=output))

    assert "找不到这个文本文件" in str(exc.value)


def test_generate_pdf_from_request_rejects_missing_output_path_with_friendly_message(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("天地", encoding="utf-8")

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=Path("")))

    assert "请选择 PDF 保存位置" in str(exc.value)


def test_generate_pdf_from_request_rejects_missing_output_directory(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("天地", encoding="utf-8")
    output = tmp_path / "missing" / "sample.pdf"

    with pytest.raises(FriendlyGenerationError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=output))

    assert "PDF 保存目录不存在" in str(exc.value)


def test_generate_pdf_from_request_uses_layout_choices(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    result = generate_pdf_from_request(
        GenerateRequest(
            text_files=[source],
            output_path=output,
            overwrite=True,
            template_key="aged",
            paper_size="a5",
            font_size="large",
            columns="fewer",
        )
    )

    reader = PdfReader(str(output))
    assert result.page_count == 1
    assert float(reader.pages[0].mediabox.width) == 420
    assert float(reader.pages[0].mediabox.height) == 595
```

Update the existing service validation tests so they expect `FriendlyGenerationError` and Chinese messages instead of `ValueError` English messages.

- [ ] **Step 2: Write failing CLI preset test**

Append to `tests/test_cli.py`:

```python
from pypdf import PdfReader


def test_cli_accepts_layout_flags(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    exit_code = main(
        [
            str(source),
            "--output",
            str(output),
            "--overwrite",
            "--template",
            "classic",
            "--paper-size",
            "a5",
            "--font-size",
            "large",
            "--columns",
            "fewer",
        ]
    )

    reader = PdfReader(str(output))
    assert exit_code == 0
    assert float(reader.pages[0].mediabox.width) == 420
    assert float(reader.pages[0].mediabox.height) == 595
```

- [ ] **Step 3: Run service and CLI tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_app_service.py tests/test_cli.py -v
```

Expected:

```text
ImportError, TypeError, or unrecognized arguments
```

- [ ] **Step 4: Implement app service preflight and choices**

Update `src/ancientbook/app_service.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.pdf import PdfGenerationError, write_pdf
from ancientbook.presets import DEFAULT_COLUMNS, DEFAULT_FONT_SIZE, DEFAULT_PAPER_SIZE, DEFAULT_TEMPLATE, build_layout_settings
from ancientbook.text_reader import TextReadError, read_text_files


class FriendlyGenerationError(ValueError):
    pass


@dataclass(frozen=True)
class GenerateRequest:
    text_files: list[Path]
    output_path: Path
    font_path: Path | None = None
    title: str = "AncientBook"
    overwrite: bool = False
    template_key: str = DEFAULT_TEMPLATE
    paper_size: str = DEFAULT_PAPER_SIZE
    font_size: str = DEFAULT_FONT_SIZE
    columns: str = DEFAULT_COLUMNS


@dataclass(frozen=True)
class GenerateResult:
    output_path: Path
    page_count: int


def _validate_request(request: GenerateRequest) -> None:
    if not request.text_files:
        raise FriendlyGenerationError("请选择至少一个文本文件。")
    for text_file in request.text_files:
        if not Path(text_file).exists():
            raise FriendlyGenerationError(f"找不到这个文本文件：{text_file}")
    if str(request.output_path).strip() in {"", "."}:
        raise FriendlyGenerationError("请选择 PDF 保存位置。")
    if request.output_path.suffix.lower() != ".pdf":
        raise FriendlyGenerationError("输出文件需要以 .pdf 结尾。")
    if request.output_path.parent and not request.output_path.parent.exists():
        raise FriendlyGenerationError("PDF 保存目录不存在。")
    if request.font_path is not None and not request.font_path.exists():
        raise FriendlyGenerationError(f"找不到这个字体文件：{request.font_path}")


def generate_pdf_from_request(request: GenerateRequest) -> GenerateResult:
    _validate_request(request)
    try:
        text = read_text_files(request.text_files)
        tokens = parse_markup(text)
        settings = build_layout_settings(request.paper_size, request.font_size, request.columns)
        placements = layout_tokens(tokens, settings)
        write_pdf(
            request.output_path,
            placements,
            settings,
            request.font_path,
            request.title,
            overwrite=request.overwrite,
            template_key=request.template_key,
        )
    except TextReadError as exc:
        raise FriendlyGenerationError("这个文本文件无法读取，请确认它是 UTF-8 文本。") from exc
    except PdfGenerationError as exc:
        message = str(exc)
        if "already exists" in message:
            raise FriendlyGenerationError("将覆盖已有 PDF。") from exc
        if "Font file" in message:
            raise FriendlyGenerationError("字体文件无法读取，请换一个字体。") from exc
        raise FriendlyGenerationError("生成失败，请换一个输出位置或检查文本文件后再试。") from exc
    page_count = max((placement.page_index for placement in placements), default=0) + 1
    return GenerateResult(output_path=request.output_path, page_count=page_count)
```

- [ ] **Step 5: Implement CLI flags**

Update `src/ancientbook/cli.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from ancientbook.app_service import FriendlyGenerationError, GenerateRequest, generate_pdf_from_request
from ancientbook.presets import COLUMN_DENSITY_CHOICES, FONT_SIZE_CHOICES, PAPER_SIZE_CHOICES, TEMPLATE_CHOICES


def _choice_keys(choices):
    return [choice.key for choice in choices]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an ancient-book-style vertical PDF.")
    parser.add_argument("text_files", nargs="+", help="UTF-8 .txt files to render")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--font", default=None, help="Optional local .ttf or .otf font path")
    parser.add_argument("--title", default="AncientBook", help="PDF title")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output PDF if it exists")
    parser.add_argument("--template", choices=_choice_keys(TEMPLATE_CHOICES), default="simple", help="Background template")
    parser.add_argument("--paper-size", choices=_choice_keys(PAPER_SIZE_CHOICES), default="a4", help="Paper size")
    parser.add_argument("--font-size", choices=_choice_keys(FONT_SIZE_CHOICES), default="medium", help="Font size preset")
    parser.add_argument("--columns", choices=_choice_keys(COLUMN_DENSITY_CHOICES), default="standard", help="Column density")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        generate_pdf_from_request(
            GenerateRequest(
                text_files=[Path(path) for path in args.text_files],
                output_path=Path(args.output),
                font_path=Path(args.font) if args.font else None,
                title=args.title,
                overwrite=args.overwrite,
                template_key=args.template,
                paper_size=args.paper_size,
                font_size=args.font_size,
                columns=args.columns,
            )
        )
    except FriendlyGenerationError as exc:
        parser.exit(2, f"AncientBook error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Run app service and CLI tests**

Run:

```powershell
python -m pytest tests/test_app_service.py tests/test_cli.py -v
```

Expected:

```text
All selected tests pass
```

- [ ] **Step 7: Commit**

Run:

```powershell
git add src/ancientbook/app_service.py src/ancientbook/cli.py tests/test_app_service.py tests/test_cli.py
git commit -m "feat: add generation preflight and CLI presets"
```

## Task 4: Persist Usability Choices

**Files:**
- Modify: `src/ancientbook/settings.py`
- Modify: `tests/test_settings.py`

- [ ] **Step 1: Write failing settings tests**

Append to `tests/test_settings.py`:

```python
def test_save_and_load_settings_with_usability_choices(tmp_path: Path):
    path = tmp_path / "settings.json"
    settings = AppSettings(
        last_text_dir=str(tmp_path / "texts"),
        last_output_dir=str(tmp_path / "out"),
        last_font_path=str(tmp_path / "font.ttf"),
        template_key="aged",
        paper_size="a5",
        font_size="large",
        columns="fewer",
    )

    save_settings(path, settings)

    assert load_settings(path) == settings


def test_load_settings_falls_back_for_invalid_choice_values(tmp_path: Path):
    path = tmp_path / "settings.json"
    path.write_text(
        '{"template_key":"bad","paper_size":"bad","font_size":"bad","columns":"bad"}',
        encoding="utf-8",
    )

    settings = load_settings(path)

    assert settings.template_key == "simple"
    assert settings.paper_size == "a4"
    assert settings.font_size == "medium"
    assert settings.columns == "standard"
```

- [ ] **Step 2: Run settings tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_settings.py -v
```

Expected:

```text
TypeError or AttributeError
```

- [ ] **Step 3: Implement persisted choices**

Update `src/ancientbook/settings.py`:

```python
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from ancientbook.presets import (
    COLUMN_DENSITY_CHOICES,
    DEFAULT_COLUMNS,
    DEFAULT_FONT_SIZE,
    DEFAULT_PAPER_SIZE,
    DEFAULT_TEMPLATE,
    FONT_SIZE_CHOICES,
    PAPER_SIZE_CHOICES,
    TEMPLATE_CHOICES,
    normalize_choice,
)


@dataclass(frozen=True)
class AppSettings:
    last_text_dir: str = ""
    last_output_dir: str = ""
    last_font_path: str = ""
    template_key: str = DEFAULT_TEMPLATE
    paper_size: str = DEFAULT_PAPER_SIZE
    font_size: str = DEFAULT_FONT_SIZE
    columns: str = DEFAULT_COLUMNS


def default_settings_path() -> Path:
    return Path.home() / ".ancientbook" / "settings.json"


def load_settings(path: Path | None = None) -> AppSettings:
    settings_path = path or default_settings_path()
    if not settings_path.exists():
        return AppSettings()
    try:
        raw = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppSettings()
    if not isinstance(raw, dict):
        return AppSettings()
    return AppSettings(
        last_text_dir=str(raw.get("last_text_dir", "")),
        last_output_dir=str(raw.get("last_output_dir", "")),
        last_font_path=str(raw.get("last_font_path", "")),
        template_key=normalize_choice(raw.get("template_key"), TEMPLATE_CHOICES, DEFAULT_TEMPLATE),
        paper_size=normalize_choice(raw.get("paper_size"), PAPER_SIZE_CHOICES, DEFAULT_PAPER_SIZE),
        font_size=normalize_choice(raw.get("font_size"), FONT_SIZE_CHOICES, DEFAULT_FONT_SIZE),
        columns=normalize_choice(raw.get("columns"), COLUMN_DENSITY_CHOICES, DEFAULT_COLUMNS),
    )


def save_settings(path: Path | None, settings: AppSettings) -> None:
    settings_path = path or default_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run settings tests**

Run:

```powershell
python -m pytest tests/test_settings.py -v
```

Expected:

```text
All selected tests pass
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/settings.py tests/test_settings.py
git commit -m "feat: persist usability choices"
```

## Task 5: Add Desktop Controls And Friendly Warnings

**Files:**
- Modify: `src/ancientbook/desktop/main_window.py`
- Modify: `src/ancientbook/desktop/worker.py`
- Modify: `tests/test_desktop_imports.py`

- [ ] **Step 1: Write failing desktop import/control tests**

Append to `tests/test_desktop_imports.py`:

```python
def test_main_window_has_usability_choice_helpers():
    from ancientbook.desktop.main_window import MainWindow

    assert hasattr(MainWindow, "_combo_for_choices")
    assert hasattr(MainWindow, "_save_choice_settings")
```

- [ ] **Step 2: Run desktop tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py::test_main_window_has_usability_choice_helpers -v
```

Expected:

```text
AssertionError
```

- [ ] **Step 3: Update worker to preserve friendly messages**

Update `src/ancientbook/desktop/worker.py`:

```python
from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ancientbook.app_service import FriendlyGenerationError, GenerateRequest, GenerateResult, generate_pdf_from_request


class GenerateWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, request: GenerateRequest):
        super().__init__()
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            result: GenerateResult = generate_pdf_from_request(self._request)
        except FriendlyGenerationError as exc:
            self.failed.emit(str(exc))
            return
        except Exception:
            self.failed.emit("生成失败，请换一个输出位置或检查文本文件后再试。")
            return
        self.finished.emit(result)
```

- [ ] **Step 4: Update desktop main window controls**

Modify `src/ancientbook/desktop/main_window.py`:

- Import `QComboBox`.
- Import choice catalogs from `ancientbook.presets`.
- Add `self.template_combo`, `self.paper_size_combo`, `self.font_size_combo`, and `self.columns_combo`.
- Add helper `_combo_for_choices(choices, selected_key)`.
- Add helper `_selected_key(combo)`.
- Add helper `_save_choice_settings()`.
- Add the four combo rows to `_build_ui`.
- In `_build_request`, pass `template_key`, `paper_size`, `font_size`, and `columns`.
- In `generate_pdf`, if no font path is selected, show `QMessageBox.warning` with text `未选择字体，中文字符可能显示不完整。仍要继续吗？` and continue only when the user confirms.
- Save choices before starting the worker.

Use this helper structure:

```python
    def _combo_for_choices(self, choices, selected_key: str) -> QComboBox:
        combo = QComboBox()
        for choice in choices:
            combo.addItem(choice.label, choice.key)
        index = combo.findData(selected_key)
        combo.setCurrentIndex(index if index >= 0 else 0)
        combo.currentIndexChanged.connect(self._save_choice_settings)
        return combo

    def _selected_key(self, combo: QComboBox) -> str:
        value = combo.currentData()
        return str(value) if value is not None else ""

    def _save_choice_settings(self) -> None:
        self._settings = AppSettings(
            last_text_dir=self._settings.last_text_dir,
            last_output_dir=self._settings.last_output_dir,
            last_font_path=self.font_edit.text().strip(),
            template_key=self._selected_key(self.template_combo),
            paper_size=self._selected_key(self.paper_size_combo),
            font_size=self._selected_key(self.font_size_combo),
            columns=self._selected_key(self.columns_combo),
        )
        save_settings(None, self._settings)
```

When updating existing `AppSettings` constructor calls in `choose_text_files`, `choose_output_file`, and `choose_font_file`, preserve the four choice fields from `self._settings`.

- [ ] **Step 5: Run desktop import tests**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py -v
```

Expected:

```text
All selected tests pass
```

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/ancientbook/desktop/main_window.py src/ancientbook/desktop/worker.py tests/test_desktop_imports.py
git commit -m "feat: add desktop usability controls"
```

## Task 6: Update Documentation And Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/release-checklists/non-programmer-acceptance.md`
- Modify: `docs/release-checklists/windows-manual-check.md`

- [ ] **Step 1: Update README**

In `README.md`, update the non-programmer workflow so steps mention:

```markdown
6. Choose a template, paper size, font size, and column density.
7. Click `Generate PDF`.
```

Add CLI example:

```powershell
ancientbook examples/sample.txt --output output/sample-a5.pdf --paper-size a5 --font-size large --columns fewer --template aged --overwrite
```

- [ ] **Step 2: Update manual checklists**

In `docs/release-checklists/non-programmer-acceptance.md` and `docs/release-checklists/windows-manual-check.md`, add checks for:

```markdown
- [ ] Choose each template at least once.
- [ ] Generate one A4 Medium Standard PDF.
- [ ] Generate one A5 Large Fewer PDF.
- [ ] Confirm the app warns when no font is selected.
```

- [ ] **Step 3: Run full test suite**

Run:

```powershell
python -m pytest -v
```

Expected:

```text
All tests pass
```

- [ ] **Step 4: Rebuild Windows app**

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

Expected:

```text
Build complete:
C:\Users\away\Documents\AncientBook\dist\AncientBook\AncientBook.exe
```

- [ ] **Step 5: Verify packaged executable launches**

Run:

```powershell
Start-Process -FilePath dist\AncientBook\AncientBook.exe -WindowStyle Hidden
Start-Sleep -Seconds 5
Get-Process | Where-Object { $_.ProcessName -like "AncientBook*" } | Select-Object -First 1 ProcessName,Id
Get-Process | Where-Object { $_.ProcessName -like "AncientBook*" } | Stop-Process
```

Expected:

```text
An AncientBook process is listed, then stopped.
```

- [ ] **Step 6: Generate CLI acceptance PDF**

Run:

```powershell
python -m ancientbook.cli examples\sample.txt --output output\sample-usability-a5.pdf --paper-size a5 --font-size large --columns fewer --template aged --overwrite
```

Expected:

```text
Exit code 0 and output\sample-usability-a5.pdf exists.
```

- [ ] **Step 7: Commit docs**

Run:

```powershell
git add README.md docs/release-checklists/non-programmer-acceptance.md docs/release-checklists/windows-manual-check.md
git commit -m "docs: update usability acceptance instructions"
```

## Final Verification

- [ ] **Step 1: Run full test suite**

Run:

```powershell
python -m pytest -v
```

Expected:

```text
All tests pass
```

- [ ] **Step 2: Verify executable exists**

Run:

```powershell
Test-Path dist\AncientBook\AncientBook.exe
```

Expected:

```text
True
```

- [ ] **Step 3: Check git status**

Run:

```powershell
git status --short --ignored
```

Expected:

```text
No tracked changes. Ignored entries may include build/, dist/, output/, caches, and egg-info.
```

## Self-Review Notes

Spec coverage:

- Template selector: Task 1, Task 2, Task 5, Task 6.
- Paper, font size, and column density choices: Task 1, Task 3, Task 4, Task 5.
- Preflight checks: Task 3.
- Friendly errors: Task 3 and Task 5.
- Settings persistence: Task 4 and Task 5.
- CLI compatibility: Task 3 and Task 6.
- Safety and compliance: Task 2 avoids assets, Task 6 keeps font and local-generation docs.

Placeholder scan:

- No incomplete implementation steps are intended to remain.

Type consistency:

- Choice keys are consistently `simple`, `classic`, `aged`, `a4`, `a5`, `small`, `medium`, `large`, `fewer`, `standard`, and `more`.
- Request fields are consistently `template_key`, `paper_size`, `font_size`, and `columns`.
