# AncientBook Desktop UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows-friendly PySide6 desktop interface that lets a non-programmer choose text files, choose an output PDF path, optionally choose a local font, and generate an AncientBook PDF with clear success or error feedback.

**Architecture:** Add a thin application service layer above the tested core PDF pipeline, then build a PySide6 UI on top of that service. The UI should not know parsing, layout, or ReportLab details; it only gathers paths and starts generation in a worker thread so the window stays responsive.

**Tech Stack:** Python 3.11+, PySide6, pytest, existing AncientBook core modules, PyInstaller deferred to the packaging follow-up plan.

---

## Scope

This plan implements the first usable desktop workflow:

```text
Open app window
Select one or more UTF-8 .txt files
Select output PDF path
Optionally select a local .ttf/.otf font
Click Generate
See success or readable error message
```

This plan does not package a final `.exe`. It prepares the project so packaging is straightforward next.

## File Structure

- `pyproject.toml`: add PySide6 dependency and desktop script entry point.
- `src/ancientbook/app_service.py`: non-UI service that validates inputs and calls the existing core pipeline.
- `src/ancientbook/settings.py`: JSON settings for last-used paths.
- `src/ancientbook/desktop/__init__.py`: desktop package marker.
- `src/ancientbook/desktop/worker.py`: background generation worker for PySide6.
- `src/ancientbook/desktop/main_window.py`: main desktop window.
- `src/ancientbook/desktop/app.py`: desktop app entry point.
- `tests/test_app_service.py`: service tests.
- `tests/test_settings.py`: settings tests.
- `tests/test_desktop_imports.py`: import smoke tests for PySide6 desktop modules.
- `README.md`: desktop development run instructions.
- `docs/superpowers/plans/2026-06-04-ancientbook-packaging-plan-notes.md`: notes for the next packaging plan.

## Task 1: Add Application Service

**Files:**
- Create: `src/ancientbook/app_service.py`
- Create: `tests/test_app_service.py`

- [ ] **Step 1: Write application service tests**

Create `tests/test_app_service.py`:

```python
from pathlib import Path

import pytest

from ancientbook.app_service import GenerateRequest, GenerateResult, generate_pdf_from_request


def test_generate_pdf_from_request_creates_pdf(tmp_path: Path):
    source = tmp_path / "sample.txt"
    output = tmp_path / "sample.pdf"
    source.write_text("天地玄黃，宇宙洪荒。", encoding="utf-8")

    result = generate_pdf_from_request(
        GenerateRequest(text_files=[source], output_path=output, overwrite=True)
    )

    assert isinstance(result, GenerateResult)
    assert result.output_path == output
    assert output.exists()
    assert output.stat().st_size > 1000


def test_generate_pdf_from_request_requires_text_files(tmp_path: Path):
    output = tmp_path / "sample.pdf"

    with pytest.raises(ValueError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[], output_path=output))

    assert "Select at least one text file" in str(exc.value)


def test_generate_pdf_from_request_requires_pdf_extension(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("天地", encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        generate_pdf_from_request(GenerateRequest(text_files=[source], output_path=tmp_path / "sample.txt"))

    assert "Output path must end with .pdf" in str(exc.value)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_app_service.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.app_service'
```

- [ ] **Step 3: Implement the service**

Create `src/ancientbook/app_service.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.model import LayoutSettings
from ancientbook.pdf import write_pdf
from ancientbook.text_reader import read_text_files


@dataclass(frozen=True)
class GenerateRequest:
    text_files: list[Path]
    output_path: Path
    font_path: Path | None = None
    title: str = "AncientBook"
    overwrite: bool = False


@dataclass(frozen=True)
class GenerateResult:
    output_path: Path
    page_count: int


def _validate_request(request: GenerateRequest) -> None:
    if not request.text_files:
        raise ValueError("Select at least one text file.")
    if request.output_path.suffix.lower() != ".pdf":
        raise ValueError("Output path must end with .pdf.")
    if request.font_path is not None and not request.font_path.exists():
        raise ValueError(f"Font file does not exist: {request.font_path}")


def generate_pdf_from_request(request: GenerateRequest) -> GenerateResult:
    _validate_request(request)
    text = read_text_files(request.text_files)
    tokens = parse_markup(text)
    settings = LayoutSettings()
    placements = layout_tokens(tokens, settings)
    write_pdf(
        request.output_path,
        placements,
        settings,
        request.font_path,
        request.title,
        overwrite=request.overwrite,
    )
    page_count = max((placement.page_index for placement in placements), default=0) + 1
    return GenerateResult(output_path=request.output_path, page_count=page_count)
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```powershell
python -m pytest tests/test_app_service.py -v
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/app_service.py tests/test_app_service.py
git commit -m "feat: add PDF generation service"
```

## Task 2: Add JSON Settings

**Files:**
- Create: `src/ancientbook/settings.py`
- Create: `tests/test_settings.py`

- [ ] **Step 1: Write settings tests**

Create `tests/test_settings.py`:

```python
from pathlib import Path

from ancientbook.settings import AppSettings, load_settings, save_settings


def test_save_and_load_settings_round_trip(tmp_path: Path):
    path = tmp_path / "settings.json"
    settings = AppSettings(
        last_text_dir=str(tmp_path / "texts"),
        last_output_dir=str(tmp_path / "out"),
        last_font_path=str(tmp_path / "font.ttf"),
    )

    save_settings(path, settings)

    assert load_settings(path) == settings


def test_load_settings_returns_defaults_when_missing(tmp_path: Path):
    assert load_settings(tmp_path / "missing.json") == AppSettings()


def test_load_settings_ignores_invalid_json(tmp_path: Path):
    path = tmp_path / "settings.json"
    path.write_text("{not json", encoding="utf-8")

    assert load_settings(path) == AppSettings()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_settings.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.settings'
```

- [ ] **Step 3: Implement settings module**

Create `src/ancientbook/settings.py`:

```python
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    last_text_dir: str = ""
    last_output_dir: str = ""
    last_font_path: str = ""


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
    )


def save_settings(path: Path | None, settings: AppSettings) -> None:
    settings_path = path or default_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```powershell
python -m pytest tests/test_settings.py -v
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/settings.py tests/test_settings.py
git commit -m "feat: persist desktop settings"
```

## Task 3: Add PySide6 Dependency And Import Smoke Tests

**Files:**
- Modify: `pyproject.toml`
- Create: `src/ancientbook/desktop/__init__.py`
- Create: `tests/test_desktop_imports.py`

- [ ] **Step 1: Write import smoke test**

Create `tests/test_desktop_imports.py`:

```python
def test_desktop_package_imports():
    import ancientbook.desktop

    assert ancientbook.desktop is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.desktop'
```

- [ ] **Step 3: Add PySide6 dependency and desktop script**

Modify `pyproject.toml` so `[project] dependencies` includes PySide6 and `[project.scripts]` includes `ancientbook-desktop`:

```toml
dependencies = [
  "Pillow>=10.4",
  "reportlab>=4.2",
  "pypdf>=4.2",
  "PySide6>=6.8",
]

[project.scripts]
ancientbook = "ancientbook.cli:main"
ancientbook-desktop = "ancientbook.desktop.app:main"
```

- [ ] **Step 4: Create desktop package**

Create `src/ancientbook/desktop/__init__.py`:

```python
"""Desktop user interface for AncientBook."""
```

- [ ] **Step 5: Install updated dependencies**

Run:

```powershell
python -m pip install -e ".[dev]"
```

Expected:

```text
Successfully installed
```

- [ ] **Step 6: Run import test to verify it passes**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py -v
```

Expected:

```text
1 passed
```

- [ ] **Step 7: Commit**

Run:

```powershell
git add pyproject.toml src/ancientbook/desktop/__init__.py tests/test_desktop_imports.py
git commit -m "feat: add desktop package"
```

## Task 4: Add Background Worker

**Files:**
- Create: `src/ancientbook/desktop/worker.py`
- Modify: `tests/test_desktop_imports.py`

- [ ] **Step 1: Add worker import test**

Append to `tests/test_desktop_imports.py`:

```python
def test_worker_imports():
    from ancientbook.desktop.worker import GenerateWorker

    assert GenerateWorker is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py::test_worker_imports -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.desktop.worker'
```

- [ ] **Step 3: Implement worker**

Create `src/ancientbook/desktop/worker.py`:

```python
from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ancientbook.app_service import GenerateRequest, GenerateResult, generate_pdf_from_request


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
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py::test_worker_imports -v
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/desktop/worker.py tests/test_desktop_imports.py
git commit -m "feat: add desktop generation worker"
```

## Task 5: Add Main Window

**Files:**
- Create: `src/ancientbook/desktop/main_window.py`
- Modify: `tests/test_desktop_imports.py`

- [ ] **Step 1: Add main window import test**

Append to `tests/test_desktop_imports.py`:

```python
def test_main_window_imports():
    from ancientbook.desktop.main_window import MainWindow

    assert MainWindow is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py::test_main_window_imports -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.desktop.main_window'
```

- [ ] **Step 3: Implement main window**

Create `src/ancientbook/desktop/main_window.py`:

```python
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ancientbook.app_service import GenerateRequest, GenerateResult
from ancientbook.desktop.worker import GenerateWorker
from ancientbook.settings import AppSettings, load_settings, save_settings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AncientBook")
        self._settings = load_settings()
        self._thread: QThread | None = None
        self._worker: GenerateWorker | None = None

        self.text_files_edit = QLineEdit()
        self.output_edit = QLineEdit()
        self.font_edit = QLineEdit(self._settings.last_font_path)
        self.status_label = QLabel("Ready")
        self.generate_button = QPushButton("Generate PDF")

        self._build_ui()
        self.generate_button.clicked.connect(self.generate_pdf)

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        form = QFormLayout()

        form.addRow("Text files", self._with_button(self.text_files_edit, "Browse", self.choose_text_files))
        form.addRow("Output PDF", self._with_button(self.output_edit, "Browse", self.choose_output_file))
        form.addRow("Font file", self._with_button(self.font_edit, "Browse", self.choose_font_file))

        root.addLayout(form)
        root.addWidget(self.generate_button)
        root.addWidget(self.status_label)
        self.setCentralWidget(central)
        self.resize(720, 240)

    def _with_button(self, line_edit: QLineEdit, label: str, callback) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        button = QPushButton(label)
        button.clicked.connect(callback)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        return widget

    def choose_text_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select text files",
            self._settings.last_text_dir,
            "Text files (*.txt);;All files (*.*)",
        )
        if files:
            self.text_files_edit.setText(";".join(files))
            self._settings = AppSettings(
                last_text_dir=str(Path(files[0]).parent),
                last_output_dir=self._settings.last_output_dir,
                last_font_path=self._settings.last_font_path,
            )
            save_settings(None, self._settings)

    def choose_output_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose output PDF",
            self._settings.last_output_dir,
            "PDF files (*.pdf)",
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path = f"{path}.pdf"
            self.output_edit.setText(path)
            self._settings = AppSettings(
                last_text_dir=self._settings.last_text_dir,
                last_output_dir=str(Path(path).parent),
                last_font_path=self._settings.last_font_path,
            )
            save_settings(None, self._settings)

    def choose_font_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose font file",
            self._settings.last_font_path,
            "Font files (*.ttf *.otf);;All files (*.*)",
        )
        if path:
            self.font_edit.setText(path)
            self._settings = AppSettings(
                last_text_dir=self._settings.last_text_dir,
                last_output_dir=self._settings.last_output_dir,
                last_font_path=path,
            )
            save_settings(None, self._settings)

    def _build_request(self) -> GenerateRequest:
        text_files = [Path(part) for part in self.text_files_edit.text().split(";") if part.strip()]
        output_path = Path(self.output_edit.text().strip())
        font_text = self.font_edit.text().strip()
        return GenerateRequest(
            text_files=text_files,
            output_path=output_path,
            font_path=Path(font_text) if font_text else None,
            overwrite=True,
        )

    def generate_pdf(self) -> None:
        request = self._build_request()
        self.generate_button.setEnabled(False)
        self.status_label.setText("Generating...")

        self._thread = QThread()
        self._worker = GenerateWorker(request)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.failed.connect(self._on_generation_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_generation_finished(self, result: GenerateResult) -> None:
        self.generate_button.setEnabled(True)
        self.status_label.setText(f"Generated: {result.output_path}")
        QMessageBox.information(self, "AncientBook", f"PDF generated:\n{result.output_path}")

    def _on_generation_failed(self, message: str) -> None:
        self.generate_button.setEnabled(True)
        self.status_label.setText("Generation failed")
        QMessageBox.critical(self, "AncientBook", message)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py::test_main_window_imports -v
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit**

Run:

```powershell
git add src/ancientbook/desktop/main_window.py tests/test_desktop_imports.py
git commit -m "feat: add desktop main window"
```

## Task 6: Add Desktop App Entry Point

**Files:**
- Create: `src/ancientbook/desktop/app.py`
- Modify: `tests/test_desktop_imports.py`
- Modify: `README.md`

- [ ] **Step 1: Add app import test**

Append to `tests/test_desktop_imports.py`:

```python
def test_desktop_app_imports():
    from ancientbook.desktop.app import main

    assert main is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py::test_desktop_app_imports -v
```

Expected:

```text
ModuleNotFoundError: No module named 'ancientbook.desktop.app'
```

- [ ] **Step 3: Implement app entry point**

Create `src/ancientbook/desktop/app.py`:

```python
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from ancientbook.desktop.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    app = QApplication(argv or sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Update README desktop instructions**

Append to `README.md`:

````markdown

## Desktop Development Run

Start the desktop UI:

```powershell
ancientbook-desktop
```

The desktop UI uses the same local PDF pipeline as the CLI. User text stays on the local machine.
````

- [ ] **Step 5: Run desktop import tests**

Run:

```powershell
python -m pytest tests/test_desktop_imports.py -v
```

Expected:

```text
4 passed
```

- [ ] **Step 6: Commit**

Run:

```powershell
git add src/ancientbook/desktop/app.py tests/test_desktop_imports.py README.md
git commit -m "feat: add desktop app entry point"
```

## Task 7: Full Verification And Packaging Notes

**Files:**
- Create: `docs/superpowers/plans/2026-06-04-ancientbook-packaging-plan-notes.md`
- Modify: `README.md`

- [ ] **Step 1: Run full test suite**

Run:

```powershell
python -m pytest -v
```

Expected:

```text
All tests pass
```

- [ ] **Step 2: Verify CLI still generates PDF**

Run:

```powershell
python -m ancientbook.cli examples/sample.txt --output output/sample.pdf --overwrite
```

Expected:

```text
No terminal error, and output/sample.pdf exists.
```

- [ ] **Step 3: Verify desktop entry point helpfully imports**

Run:

```powershell
python -c "from ancientbook.desktop.app import main; print(callable(main))"
```

Expected:

```text
True
```

- [ ] **Step 4: Create packaging notes**

Create `docs/superpowers/plans/2026-06-04-ancientbook-packaging-plan-notes.md`:

```markdown
# AncientBook Packaging Plan Notes

The next plan should package the desktop app for Windows.

Recommended next tasks:

1. Add PyInstaller as a development dependency.
2. Add a reproducible build command for `ancientbook.desktop.app`.
3. Include dependency license notes for PySide6, Pillow, ReportLab, and pypdf.
4. Confirm no fonts are bundled by default.
5. Build a Windows executable locally.
6. Run the executable and generate a PDF from `examples/sample.txt`.
7. Document the non-programmer workflow in README.
```

- [ ] **Step 5: Update README status**

Append to `README.md`:

```markdown

## Implemented Desktop Slice

The first desktop slice can:

- Select text files.
- Select an output PDF path.
- Optionally select a local font file.
- Generate a PDF through the tested local core pipeline.
- Show success and error messages in the app.

Packaging as a Windows executable is planned next.
```

- [ ] **Step 6: Commit**

Run:

```powershell
git add README.md docs/superpowers/plans/2026-06-04-ancientbook-packaging-plan-notes.md
git commit -m "docs: record desktop verification and packaging follow-up"
```

## Self-Review Notes

Spec coverage:

- Desktop file selection: covered by Task 5.
- Optional local font selection: covered by Task 5.
- Output path selection: covered by Task 5.
- Generate button: covered by Task 5.
- Friendly success and error messages: covered by Task 5.
- Worker thread for responsiveness: covered by Task 4 and Task 5.
- Settings persistence: covered by Task 2 and Task 5.
- Reuse of safe local core pipeline: covered by Task 1 and Task 5.
- Packaging: intentionally deferred to next plan and documented in Task 7.

Red-flag scan:

- No unresolved placeholder instructions remain.

Type consistency:

- `GenerateRequest`, `GenerateResult`, `GenerateWorker`, and `MainWindow` names are consistent across tasks.
