# Windows Manual Release Check

Use this checklist after building `dist\AncientBook\AncientBook.exe`.

- [ ] Run `powershell -ExecutionPolicy Bypass -File scripts/package_windows_release.ps1 -SkipBuild`.
- [ ] Confirm `release\AncientBook-Windows.zip` is created.
- [ ] Unzip it and confirm `README-FIRST.txt`, `examples\sample.txt`, and `licenses\THIRD_PARTY_NOTICES.md` are included.
- [ ] Launch `dist\AncientBook\AncientBook.exe`.
- [ ] Confirm the executable uses the AncientBook icon.
- [ ] Confirm the window uses a left settings panel, right page preview, and bottom status area.
- [ ] Select one or more documents, such as `examples\sample.txt`.
- [ ] Confirm the file picker lists `.txt`, `.md`, `.docx`, `.pdf`, `.rtf`, `.html`, `.odt`, and `.doc`.
- [ ] Select an output folder, such as `output`.
- [ ] Choose an installed Windows Chinese font from the Font list.
- [ ] Choose `Custom font file` and confirm a local `.ttf` or `.otf` font can still be selected.
- [ ] Choose `素雅书页`, `朱栏格页`, and `旧藏纸页` at least once.
- [ ] Confirm the right-side preview updates when changing templates, paper size, font size, and column density.
- [ ] Confirm the vermilion template has red ruled framing.
- [ ] Confirm the aged template has visible old-paper texture while the text remains readable.
- [ ] Generate once from a `.docx` document.
- [ ] Select a legacy `.doc` file and confirm the app asks the user to save it as `.docx`.
- [ ] Select a scanned or blank `.pdf` and confirm the app says OCR is not supported yet.
- [ ] Generate one A4 中字 标准 PDF.
- [ ] Generate one A5 大字 疏朗 PDF.
- [ ] Confirm the app warns if no usable system or custom font is available.
- [ ] Click `生成 PDF`.
- [ ] Confirm the app shows a success message.
- [ ] Open the generated PDF.
- [ ] Confirm `examples\sample.txt` generated `output\sample-AncientBook.pdf`.
- [ ] Generate again and confirm the app creates `output\sample-AncientBook-2.pdf` instead of overwriting the first PDF.
- [ ] Confirm the text is vertical and the page has an ancient-book-style background with paper texture and framed page styling.
- [ ] Confirm no bundled font files were added to the repository.
