# AncientBook

AncientBook is a clean-room Python desktop-tool project for generating Chinese ancient-book-style vertical PDFs from plain text.

Current status: core PDF pipeline planning and implementation.

Safety principles:

- User text stays local.
- User text is treated as data, never as code.
- Fonts are selected by the user and are not bundled unless their licenses allow redistribution.
- The project does not copy vRain source code.

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

## Implemented Core Slice

The first core slice can:

- Read UTF-8 text files.
- Parse `【comment】`, `%`, `$`, and `@`.
- Lay out text vertically from right to left.
- Draw a simple ancient-book-style page background.
- Generate a PDF locally.

The desktop interface, user settings, richer templates, and Windows packaging are planned next.

## Desktop Development Run

Start the desktop UI:

```powershell
ancientbook-desktop
```

The desktop UI uses the same local PDF pipeline as the CLI. User text stays on the local machine.

## Implemented Desktop Slice

The first desktop slice can:

- Select text files.
- Select an output PDF path.
- Optionally select a local font file.
- Generate a PDF through the tested local core pipeline.
- Show success and error messages in the app.

Packaging as a Windows executable is planned next.

## Font And License Notes

AncientBook does not bundle commercial or unknown-license fonts. Choose a local font file that you have the right to use.

Third-party dependency notes are in `docs/licenses/THIRD_PARTY_NOTICES.md`.

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

## Non-Programmer Workflow

After receiving a built `dist\AncientBook` folder:

1. Open `AncientBook.exe`.
2. Choose one or more `.txt` files.
3. Choose where to save the PDF.
4. Choose a local font file if Chinese characters do not render correctly.
5. Click `Generate PDF`.

The app works locally and does not upload your text.
