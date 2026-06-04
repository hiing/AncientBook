# AncientBook Windows Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the PySide6 AncientBook desktop app into a Windows executable folder that a non-programmer can open and use locally.

**Architecture:** Use PyInstaller in one-folder mode first because it is easier to inspect and debug than one-file mode. Keep build scripts and documentation in the repository, but keep generated `build/`, `dist/`, and output PDFs ignored so release artifacts are not accidentally committed.

**Tech Stack:** Python 3.11+, PyInstaller, PySide6, existing AncientBook desktop entry point, pytest.

---

## Scope

This plan packages the existing desktop app. It does not add new UI features, an installer, code signing, auto-updates, or bundled fonts.

The packaged app should:

- Build with a repeatable PowerShell command.
- Launch as a Windows desktop program.
- Let the user choose their own `.txt` files and local font file.
- Generate PDFs locally.
- Avoid bundling commercial or unknown-license fonts.
- Include basic license and usage notes.

## File Structure

- `pyproject.toml`: add PyInstaller to development dependencies.
- `scripts/build_windows.ps1`: repeatable Windows packaging script.
- `docs/licenses/THIRD_PARTY_NOTICES.md`: dependency notice summary for redistributed libraries.
- `README.md`: non-programmer run instructions and build instructions.
- `tests/test_packaging_files.py`: tests for packaging script and notices.

Generated but not committed:

- `build/`
- `dist/`
- `output/`

## Task 1: Add Packaging Metadata And Script

**Files:**
- Modify: `pyproject.toml`
- Create: `scripts/build_windows.ps1`
- Create: `tests/test_packaging_files.py`

- [ ] **Step 1: Write packaging file tests**

Create `tests/test_packaging_files.py`:

```python
from pathlib import Path


def test_windows_build_script_exists_and_targets_desktop_app():
    script = Path("scripts/build_windows.ps1")

    assert script.exists()
    text = script.read_text(encoding="utf-8")
    assert "PyInstaller" in text
    assert "ancientbook.desktop.app" in text
    assert "--name AncientBook" in text


def test_pyinstaller_is_dev_dependency():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert '"pyinstaller>=6.10"' in pyproject
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/test_packaging_files.py -v
```

Expected:

```text
AssertionError
```

The script does not exist and PyInstaller is not listed yet.

- [ ] **Step 3: Add PyInstaller development dependency**

Modify `pyproject.toml` so `[project.optional-dependencies] dev` becomes:

```toml
[project.optional-dependencies]
dev = [
  "pytest>=8.2",
  "pyinstaller>=6.10",
]
```

- [ ] **Step 4: Create Windows build script**

Create `scripts/build_windows.ps1`:

```powershell
$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

Write-Host "Installing AncientBook development dependencies..."
python -m pip install -e ".[dev]"

Write-Host "Removing previous build artifacts..."
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist\AncientBook") {
    Remove-Item -Recurse -Force "dist\AncientBook"
}

Write-Host "Building AncientBook desktop app with PyInstaller..."
python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name AncientBook `
    --collect-all PySide6 `
    --distpath dist `
    --workpath build `
    --specpath build `
    -m ancientbook.desktop.app

$ExePath = Join-Path $ProjectRoot "dist\AncientBook\AncientBook.exe"
if (-not (Test-Path $ExePath)) {
    throw "Build failed: AncientBook.exe was not created."
}

Write-Host "Build complete:"
Write-Host $ExePath
```

- [ ] **Step 5: Run tests to verify they pass**

Run:

```powershell
python -m pytest tests/test_packaging_files.py -v
```

Expected:

```text
2 passed
```

- [ ] **Step 6: Commit**

Run:

```powershell
git add pyproject.toml scripts/build_windows.ps1 tests/test_packaging_files.py
git commit -m "build: add Windows packaging script"
```

## Task 2: Add License And Font Safety Documentation

**Files:**
- Create: `docs/licenses/THIRD_PARTY_NOTICES.md`
- Modify: `README.md`
- Modify: `tests/test_packaging_files.py`

- [ ] **Step 1: Add documentation tests**

Append to `tests/test_packaging_files.py`:

```python
def test_third_party_notices_cover_packaged_dependencies():
    notice = Path("docs/licenses/THIRD_PARTY_NOTICES.md")

    assert notice.exists()
    text = notice.read_text(encoding="utf-8")
    for name in ["PySide6", "Pillow", "ReportLab", "pypdf", "PyInstaller"]:
        assert name in text
    assert "Fonts are not bundled" in text
```

- [ ] **Step 2: Run new test to verify it fails**

Run:

```powershell
python -m pytest tests/test_packaging_files.py::test_third_party_notices_cover_packaged_dependencies -v
```

Expected:

```text
AssertionError
```

The notice file does not exist yet.

- [ ] **Step 3: Create third-party notices**

Create `docs/licenses/THIRD_PARTY_NOTICES.md`:

```markdown
# Third-Party Notices

AncientBook is a clean-room Python implementation. It does not copy vRain source code.

Packaged runtime dependencies may include:

- PySide6: Qt for Python bindings. Review Qt for Python licensing before public redistribution.
- Pillow: Python Imaging Library fork.
- ReportLab: PDF generation library.
- pypdf: PDF inspection and manipulation library used in tests.
- PyInstaller: packaging tool used to build the Windows app.

Fonts are not bundled by default. Users choose local fonts installed on their own machine or font files they have the right to use.

Before publishing a public release, review the exact installed package versions and their license files from the build environment.
```

- [ ] **Step 4: Update README safety note**

Append to `README.md`:

```markdown

## Font And License Notes

AncientBook does not bundle commercial or unknown-license fonts. Choose a local font file that you have the right to use.

Third-party dependency notes are in `docs/licenses/THIRD_PARTY_NOTICES.md`.
```

- [ ] **Step 5: Run documentation test**

Run:

```powershell
python -m pytest tests/test_packaging_files.py::test_third_party_notices_cover_packaged_dependencies -v
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit**

Run:

```powershell
git add README.md docs/licenses/THIRD_PARTY_NOTICES.md tests/test_packaging_files.py
git commit -m "docs: add packaging license notices"
```

## Task 3: Build Windows App

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`

- [ ] **Step 1: Confirm generated build outputs are ignored**

Run:

```powershell
git check-ignore build dist output
```

Expected:

```text
build
dist
output
```

If `build`, `dist`, or `output` are not ignored, update `.gitignore` to contain:

```gitignore
dist/
build/
output/
```

- [ ] **Step 2: Run full test suite before building**

Run:

```powershell
python -m pytest -v
```

Expected:

```text
All tests pass
```

- [ ] **Step 3: Run Windows build script**

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

Expected:

```text
Build complete:
...\dist\AncientBook\AncientBook.exe
```

- [ ] **Step 4: Verify executable exists**

Run:

```powershell
Test-Path dist\AncientBook\AncientBook.exe
```

Expected:

```text
True
```

- [ ] **Step 5: Update README build instructions**

Append to `README.md`:

````markdown

## Build Windows Desktop App

Build the desktop app:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

After a successful build, open:

```text
dist\AncientBook\AncientBook.exe
```

The generated `dist/` folder is a build artifact and is not committed to git.
````

- [ ] **Step 6: Commit README or gitignore changes**

Run:

```powershell
git add README.md .gitignore
git commit -m "docs: add Windows build instructions"
```

If `.gitignore` did not change, `git add .gitignore` is harmless.

## Task 4: Manual Packaged App Verification

**Files:**
- Modify: `README.md`
- Create: `docs/release-checklists/windows-manual-check.md`

- [ ] **Step 1: Create manual checklist**

Create `docs/release-checklists/windows-manual-check.md`:

```markdown
# Windows Manual Release Check

Use this checklist after building `dist\AncientBook\AncientBook.exe`.

- [ ] Launch `dist\AncientBook\AncientBook.exe`.
- [ ] Select one or more UTF-8 `.txt` files.
- [ ] Select an output `.pdf` path.
- [ ] Optionally select a local `.ttf` or `.otf` font.
- [ ] Click Generate PDF.
- [ ] Confirm the app shows a success message.
- [ ] Open the generated PDF.
- [ ] Confirm the text is vertical and the page has an ancient-book-style background.
- [ ] Confirm no bundled font files were added to the repository.
```

- [ ] **Step 2: Verify packaged executable can be launched**

Run:

```powershell
Start-Process -FilePath dist\AncientBook\AncientBook.exe -WindowStyle Hidden
Start-Sleep -Seconds 5
Get-Process | Where-Object { $_.ProcessName -like "AncientBook*" } | Select-Object -First 1 ProcessName,Id
```

Expected:

```text
An AncientBook process is listed.
```

Then close it:

```powershell
Get-Process | Where-Object { $_.ProcessName -like "AncientBook*" } | Stop-Process
```

- [ ] **Step 3: Update README non-programmer workflow**

Append to `README.md`:

```markdown

## Non-Programmer Workflow

After receiving a built `dist\AncientBook` folder:

1. Open `AncientBook.exe`.
2. Choose one or more `.txt` files.
3. Choose where to save the PDF.
4. Choose a local font file if Chinese characters do not render correctly.
5. Click `Generate PDF`.

The app works locally and does not upload your text.
```

- [ ] **Step 4: Commit checklist and README**

Run:

```powershell
git add README.md docs/release-checklists/windows-manual-check.md
git commit -m "docs: add Windows manual release checklist"
```

## Task 5: Final Verification

**Files:**
- No source changes expected.

- [ ] **Step 1: Run full test suite**

Run:

```powershell
python -m pytest -v
```

Expected:

```text
All tests pass
```

- [ ] **Step 2: Verify package output exists**

Run:

```powershell
Test-Path dist\AncientBook\AncientBook.exe
```

Expected:

```text
True
```

- [ ] **Step 3: Confirm generated artifacts are not staged**

Run:

```powershell
git status --short --ignored
```

Expected:

```text
No tracked changes. Ignored entries may include build/, dist/, output/, __pycache__, and egg-info.
```

- [ ] **Step 4: Record final result in final response**

Report:

- Test count and pass status.
- Executable path.
- Whether manual launch check succeeded.
- Reminder that fonts are not bundled.

## Self-Review Notes

Spec coverage:

- PyInstaller packaging: covered by Task 1 and Task 3.
- Repeatable build command: covered by `scripts/build_windows.ps1`.
- Dependency license notes: covered by Task 2.
- No bundled fonts: covered by Task 2 and Task 4.
- Local executable verification: covered by Task 4 and Task 5.
- Non-programmer workflow: covered by Task 4.

Red-flag scan:

- No unresolved placeholder instructions remain.

Type consistency:

- No new Python API types are introduced in this plan.
