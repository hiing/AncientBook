# AncientBook Usability Enhancement Design

## Purpose

This slice makes the existing AncientBook desktop app easier for a non-programmer to use. The user should be able to choose a few plain-language options, generate a PDF, and understand any warning without seeing code-oriented messages.

This remains a clean-room Python implementation. It does not copy vRain source code, does not bundle fonts, and does not upload user text.

## Scope

Included:

- Add a desktop template selector with three built-in choices:
  - Simple paper.
  - Classic frame.
  - Light aged paper.
- Add plain-language layout settings:
  - Paper size: A4 or A5.
  - Font size: Small, Medium, or Large.
  - Column density: Fewer, Standard, or More.
- Add generation preflight checks before the PDF job starts.
- Convert common generation failures into user-facing messages written in ordinary language.
- Persist the selected template and layout choices in local settings.
- Keep CLI compatibility by adding optional flags for the same layout choices.

Deferred:

- Live preview.
- Full template editor.
- Automatic table of contents.
- Automatic font fallback.
- Bundled Chinese fonts.
- Advanced vRain-style notes and frames.
- PDF compression.

## User Flow

The desktop app should show the user one straightforward workflow:

```text
Open AncientBook.exe
Choose text files
Choose output PDF
Optionally choose a local font
Choose template
Choose paper size, font size, and column density
Click Generate PDF
Read a clear success, warning, or error message
```

The default choices should generate a reasonable PDF without requiring the user to understand page metrics.

## Desktop Controls

The main window will add four controls below the existing file and font inputs:

- Template: Simple paper, Classic frame, Light aged paper.
- Paper size: A4, A5.
- Font size: Small, Medium, Large.
- Columns: Fewer, Standard, More.

The labels should stay plain and non-technical. The app should not show raw point sizes, page dimensions, or internal template IDs in the visible UI.

## Layout Presets

The app will translate plain-language choices into existing core settings.

Paper size:

- A4: 595 by 842 points.
- A5: 420 by 595 points.

Font size:

- Small: 16 point body text, 8 point comment text.
- Medium: 18 point body text, 9 point comment text.
- Large: 22 point body text, 11 point comment text.

Column density:

- Fewer: 10 columns.
- Standard: 12 columns.
- More: 14 columns.

Rows should be calculated from page height and font size so text does not become obviously cramped. If a future implementation needs a fixed mapping for stability, it should keep Medium A4 Standard equivalent to the current default of 12 columns and 24 rows.

## Template Behavior

The template module will expose a small, named template catalog. Each template must be generated locally with Pillow and must not use copyrighted image assets.

Expected first templates:

- Simple paper: current basic paper background.
- Classic frame: paper background with a restrained rectangular book frame.
- Light aged paper: slightly warmer paper tone with subtle texture.

All templates must keep the same page dimensions as the layout engine.

## Preflight Checks

Before starting generation, the app should check:

- At least one text file was selected.
- Every selected text file exists.
- The output path is present and ends with `.pdf`.
- The output directory exists.
- If a font path is present, the font file exists.
- If no font path is present, show a warning that Chinese characters may not render correctly, with a way to continue.

The preflight should prevent obvious failures before the background worker starts.

## Friendly Error Messages

Common errors should be translated into ordinary language:

- Missing text file: `找不到这个文本文件。`
- Unreadable text file: `这个文本文件无法读取，请确认它是 UTF-8 文本。`
- Missing output path: `请选择 PDF 保存位置。`
- Invalid output extension: `输出文件需要以 .pdf 结尾。`
- Output directory missing: `PDF 保存目录不存在。`
- Existing PDF overwrite path: `将覆盖已有 PDF。`
- Missing font file: `找不到这个字体文件。`
- Unreadable font file: `字体文件无法读取，请换一个字体。`
- Generic generation failure: `生成失败，请换一个输出位置或检查文本文件后再试。`

The detailed internal exception can still be logged or kept in tests, but the desktop message box should lead with the friendly message.

## Settings Persistence

The settings file should remember:

- Last text directory.
- Last output directory.
- Last font path.
- Last template choice.
- Last paper size choice.
- Last font size choice.
- Last column density choice.

Invalid or obsolete saved values should fall back to defaults instead of crashing.

## CLI Compatibility

The CLI will remain usable for testing and users who prefer commands. It should accept optional flags for:

- `--template`
- `--paper-size`
- `--font-size`
- `--columns`

Defaults should match the desktop defaults.

## Testing

Core tests should cover:

- Preset choices map to expected `LayoutSettings`.
- Invalid saved settings fall back to defaults.
- Template catalog contains the three expected templates.
- Each template creates a background with the requested page dimensions.
- App service rejects missing text files and invalid output paths with friendly messages.
- CLI flags create a PDF with the requested layout.

Desktop import tests should continue to verify that PySide6 modules are importable without launching the event loop.

Manual checks should cover:

- Open packaged `AncientBook.exe`.
- Select `examples\sample.txt`.
- Choose each template at least once.
- Generate one A4 Medium Standard PDF.
- Generate one A5 Large Fewer PDF.
- Confirm the app warns when no font is selected.
- Confirm generated PDFs remain local.

## Safety And Compliance

- Do not copy vRain source code.
- Do not bundle commercial or unknown-license fonts.
- Do not upload text or font files.
- Treat user text as data only.
- Generate templates procedurally or from repository-owned assets only.
- Keep generated build outputs ignored by git.

## Acceptance Criteria

This slice is complete when:

- A non-programmer can choose template, paper size, font size, and column density from the desktop app.
- The same choices can be used from CLI flags.
- The app catches common setup mistakes before generation starts.
- Friendly user-facing messages are shown for common failures.
- Settings persist and tolerate invalid saved values.
- Full tests pass.
- A packaged Windows app can still be built and launched.
