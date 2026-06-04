# AncientBook Python Desktop Design

## Purpose

AncientBook will be a Windows-friendly desktop tool for making Chinese ancient-book-style vertical PDF ebooks from plain text. It follows the same broad goal as vRain: reproduce an ancient printed-book reading experience while keeping the output as a text-based PDF where possible, so readers can search and copy text.

This project will be a clean-room reimplementation. It may study vRain's public behavior, documentation, file concepts, and MIT license, but it will not copy Perl source code into the new implementation.

## Confirmed Direction

- Build a desktop application first.
- Use Python as the main implementation language.
- Use PySide6 for the graphical interface.
- Use ReportLab for first-version PDF generation.
- Use Pillow for generated page backgrounds.
- Store user settings in local JSON files.
- Package the finished app as a Windows executable with PyInstaller.

The intended user flow is:

```text
Open AncientBook.exe
Select one or more text files
Choose a font
Choose a page template
Click Generate
Receive a PDF
```

## First Version Scope

The first version should focus on a stable and usable baseline rather than matching every advanced vRain feature.

Included:

- Read one or more `.txt` files.
- Support UTF-8 text input.
- Generate right-to-left vertical Chinese layout.
- Fill each vertical column from top to bottom.
- Automatically create new pages when a page is full.
- Provide two or three built-in page templates.
- Let the user choose a local font file.
- Support basic punctuation handling, including an option to normalize or hide selected modern punctuation.
- Support simple inline comments marked as `【comment】`.
- Support a few simple layout markers:
  - `%` for a full-page break.
  - `$` for a next-column break in the first version.
  - `@` for a blank character slot.
- Generate a PDF that keeps text searchable where the chosen PDF/font path supports it.
- Show clear user-facing error messages when input files, fonts, or output paths are invalid.

Deferred:

- Multi-font automatic glyph fallback.
- Font metric adjustment.
- Fallback font synthetic bolding.
- Wave-line book title marks.
- Rounded frames, circle frames, point notes, line notes, and circle notes.
- Ghostscript PDF compression.
- Full template editor.
- Advanced automatic table-of-contents recognition.
- High-fidelity reproduction of every vRain configuration option.

## Main Modules

### Desktop Interface

The interface presents the workflow in plain language. It lets the user pick input files, a font, a template, and an output location. It also displays progress and clear errors.

The interface should not expose raw code concepts. Advanced settings can be added later behind a separate panel.

### Text Reader

The text reader loads `.txt` files safely. It treats all input as text data, not executable instructions.

Responsibilities:

- Read UTF-8 text.
- Merge multiple files in user-selected order.
- Remove unsafe or unsupported control characters.
- Preserve supported layout markers.
- Report unreadable files clearly.

### Markup Parser

The parser turns supported markers into structured layout instructions.

First-version markers:

- `【...】` becomes a comment attached near the surrounding正文.
- `%` becomes a full-page break.
- `$` moves layout to the next vertical column. If the current page has no remaining column, it creates a new page.
- `@` becomes a blank character slot.

Unsupported special markers remain visible as normal text and also appear in a non-blocking warning list after generation. This avoids silently deleting source text.

### Layout Engine

The layout engine calculates where each character should be placed.

Responsibilities:

- Determine page size, margins, columns, and rows.
- Place columns from right to left.
- Place characters from top to bottom.
- Start a new page when the current page is full.
- Reserve space for simple comments.
- Return structured placement data for the PDF generator.

This module should not know about the desktop interface. That separation keeps the core testable and easier to maintain.

### Background Templates

The template module creates page backgrounds such as a simple paper style or carved-book frame style.

Responsibilities:

- Draw background images with Pillow.
- Keep page dimensions consistent with the layout engine.
- Provide a small set of built-in templates.
- Avoid requiring copyrighted images.

### PDF Generator

The PDF generator combines background pages and text placements into a PDF.

Responsibilities:

- Embed or reference the selected font according to library capability and license constraints.
- Draw text in the calculated positions.
- Add generated background images.
- Preserve searchable text where possible.
- Set basic PDF metadata such as title and creator.
- Write the output file safely without overwriting unexpected files.

### Configuration

The configuration module saves local preferences.

Examples:

- Last selected font path.
- Last output directory.
- Last selected template.
- Page size and basic layout settings.

Settings should be stored as JSON in a local app data path or inside a clearly named project settings file during development.

### Packaging

Packaging should create a Windows executable that a non-programmer can run.

Responsibilities:

- Build with PyInstaller.
- Include required open-source dependency notices.
- Avoid bundling fonts unless their licenses explicitly allow redistribution.
- Provide a simple README for end users.

## Safety And Compliance

- Do not copy vRain source code into this project.
- Keep vRain attribution in design notes where its goals or public documentation informed the project.
- Review third-party library licenses before release.
- Do not bundle commercial or unknown-license fonts.
- Do not upload user text anywhere.
- Do not run code from user-provided text.
- Keep generation local by default.
- Validate file paths before writing output.
- Show clear warnings before overwriting an existing PDF.

## Development Order

1. Create the project skeleton and dependency files.
2. Build a minimal core that converts sample text into placement data.
3. Add a basic PDF generator with one page template and one selected font.
4. Add text file loading and simple marker parsing.
5. Add the desktop interface.
6. Add two or three templates.
7. Add friendly error messages and settings persistence.
8. Add packaging and user documentation.
9. Test with short and medium Chinese texts.

Each step should produce something visible:

- After step 2, a text layout preview can be inspected in tests.
- After step 3, a PDF can be generated from a hard-coded sample.
- After step 5, the user can operate the tool through a window.
- After step 8, the user can run a packaged app.

## Later Decisions

- Which exact open-source Chinese font to recommend in documentation.
- Whether the first preview should be a PDF-only preview or an in-app image preview.
