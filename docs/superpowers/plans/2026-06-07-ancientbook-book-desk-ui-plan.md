# AncientBook Book Desk UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the desktop window from a plain form into a calm book-desk interface with left-side controls, a right-side ancient-page preview, and a bottom status area.

**Architecture:** Keep the conversion pipeline unchanged. Add a small desktop preview module that renders a scaled PIL image from the existing PDF template functions, then display it in the PySide6 main window.

**Tech Stack:** Python 3.11, PySide6, Pillow, pytest.

---

### Task 1: Add Preview Tests

**Files:**
- Create: `tests/test_desktop_preview.py`
- Modify: `tests/test_desktop_imports.py`

- [ ] Write a failing test that imports `ancientbook.desktop.preview.create_preview_image` and checks it returns a scaled image.
- [ ] Write a failing test that instantiates `MainWindow` and checks for `ControlPanel`, `PreviewPanel`, `PrimaryButton`, and a non-empty preview pixmap.
- [ ] Run the focused tests and confirm they fail because the preview module and UI objects do not exist yet.

### Task 2: Add Preview Rendering

**Files:**
- Create: `src/ancientbook/desktop/preview.py`

- [ ] Implement `create_preview_image(template_key, paper_size, font_size, columns, max_height=430)` with existing `build_layout_settings` and `create_background`.
- [ ] Draw simple vertical ink strokes into the preview so the user sees the ancient-page direction without rendering real document text.
- [ ] Add `pixmap_from_image(image)` for the PySide6 UI.
- [ ] Run `python -m pytest tests\test_desktop_preview.py -v`.

### Task 3: Restyle Main Window

**Files:**
- Modify: `src/ancientbook/desktop/main_window.py`

- [ ] Add `PreviewPanel`.
- [ ] Rebuild `_build_ui()` into a header, left control panel, right preview panel, and bottom status bar.
- [ ] Apply an AncientBook stylesheet with paper, ink, muted green, and vermilion accents.
- [ ] Connect choice combos to `_refresh_preview()`.
- [ ] Run the focused desktop tests.

### Task 4: Verify And Package

**Files:**
- Modify: `README.md`
- Modify: `docs/release-checklists/non-programmer-acceptance.md`

- [ ] Mention the two-column book-desk interface and preview.
- [ ] Run `python -m pytest -v`.
- [ ] Build and smoke-test the exe.
- [ ] Recreate the Windows release zip.
