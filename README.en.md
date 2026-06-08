# AncientBook

[中文说明](README.md)

AncientBook is a clean-room Python desktop-tool project for generating Chinese ancient-book-style vertical PDFs from common document files.

Current status: core PDF pipeline, desktop UI, and Windows folder packaging are implemented.

Safety principles:

- User text stays local.
- User text is treated as data, never as code.
- Fonts come from installed system fonts or user-selected files; AncientBook does not bundle commercial or unknown-license fonts.
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

Generate an A5 sample with a different layout preset:

```powershell
ancientbook examples/sample.txt --output output/sample-a5.pdf --paper-size a5 --font-size large --columns fewer --template aged --overwrite
```

Use `--font C:\Path\To\YourFont.ttf` in the CLI when you want a specific local font file. The desktop app can use common installed Windows Chinese fonts directly.

Supported document inputs:

- `.txt`, `.text`
- `.md`, `.markdown`
- `.docx`
- `.pdf` files with selectable text
- `.rtf`
- `.html`, `.htm`
- `.odt`

Legacy `.doc` files are detected, but AncientBook asks you to save them as `.docx` first. Scanned PDF files need OCR and are not converted automatically in this version.

## Implemented Core Slice

The current core slice can:

- Read common document files and extract plain text locally.
- Parse `【comment】`, `%`, `$`, and `@`.
- Lay out text vertically from right to left.
- Draw ancient-book-style backgrounds with paper grain, ruled frames, and aged-paper details.
- Generate a PDF locally.

The desktop interface, user settings, richer page templates, and Windows folder packaging are implemented. The desktop window uses a book-desk layout: controls on the left, an ancient-page preview on the right, and status feedback at the bottom.

## Desktop Development Run

Start the desktop UI:

```powershell
ancientbook-desktop
```

The desktop UI uses the same local PDF pipeline as the CLI. User text stays on the local machine.

## Implemented Desktop Slice

The desktop app can:

- Select document files.
- Select an output folder.
- Choose a common installed Windows Chinese font, or select a local font file manually.
- Choose a template, paper size, font size, and column density.
- Preview the selected ancient-page style before generating.
- Generate a PDF through the tested local core pipeline.
- Show success and error messages in the app.

Windows folder packaging is implemented with PyInstaller.

The Windows app icon is stored at `assets\icon\AncientBook.ico`, with the editable PNG source at `assets\icon\AncientBook-icon.png`.

## Font And License Notes

AncientBook does not bundle commercial or unknown-license fonts. The desktop app uses installed system fonts when available, and still lets you choose a local font file that you have the right to use.

Third-party dependency notes are in `docs/licenses/THIRD_PARTY_NOTICES.md`.

## License

AncientBook is released under the MIT License. See `LICENSE`.

Third-party libraries keep their own licenses. Before redistributing a packaged build, review `docs/licenses/THIRD_PARTY_NOTICES.md` and the license files included with the packaged dependencies.

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

## Package Windows Release Zip

Create a user-facing Windows zip package:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_windows_release.ps1
```

If `dist\AncientBook\AncientBook.exe` already exists and you only want to create the zip again:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_windows_release.ps1 -SkipBuild
```

The zip is created at:

```text
release\AncientBook-Windows.zip
```

The release zip contains `AncientBook.exe`, its runtime files, a quick-start `README-FIRST.txt`, the MIT `LICENSE`, `README-project.md`, `README.en.md`, the sample file, and third-party license notes.

## Non-Programmer Workflow

After receiving `release\AncientBook-Windows.zip`, unzip it and open the `AncientBook-Windows` folder. Then:

1. Open `AncientBook.exe`.
2. Click `选择` beside `文档` and choose one or more documents. For a first check, use `examples\sample.txt`.
3. Click `选择` beside `输出文件夹` and choose an output folder, for example `output`.
4. Choose a font from the Font list, such as `微软雅黑 / Microsoft YaHei` or `宋体 / SimSun`. Use `手动选择字体文件 / Custom font file` only when you want to browse for your own `.ttf` or `.otf` file.
5. Choose a template, paper size, font size, and column density. The preview updates as these choices change.
6. If no usable system or custom font is found, confirm the warning dialog before continuing.
7. Click `生成 PDF`.

The desktop app creates the PDF automatically in the chosen folder. For example, `examples\sample.txt` becomes `output\sample-AncientBook.pdf`. If that file already exists, the app uses the next safe name, such as `output\sample-AncientBook-2.pdf`.

Supported input formats are `.txt`, `.md`, `.docx`, selectable-text `.pdf`, `.rtf`, `.html`, and `.odt`. Old `.doc` files should be saved as `.docx` first.

Template choices are `素雅书页`, `朱栏格页`, and `旧藏纸页`.

The app works locally and does not upload your text.

For a more explicit first-run checklist, see `docs/release-checklists/non-programmer-acceptance.md`.

## Quick Acceptance Check

Use this check after a Windows build:

```powershell
Test-Path dist\AncientBook\AncientBook.exe
python -m ancientbook.cli examples\sample.txt --output output\sample-acceptance.pdf --overwrite
```

Then open `output\sample-acceptance.pdf` and confirm the text is vertical with an ancient-book-style page background, including paper texture and framed page styling.
