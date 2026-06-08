# Non-Programmer Acceptance Check

This check is for a person who receives `release\AncientBook-Windows.zip` and does not need to know Python.

## First Run

1. Unzip `AncientBook-Windows.zip`.
2. Open `AncientBook-Windows\AncientBook.exe`.
3. Click `选择` beside `文档` and choose `examples\sample.txt`.
4. Click `选择` beside `输出文件夹` and choose `output`.
5. Choose a common installed Windows Chinese font from the Font list, such as `微软雅黑 / Microsoft YaHei` or `宋体 / SimSun`, or use `自选字体` to browse for a local `.ttf` or `.otf` font you have the right to use.
6. Choose a template, paper size, font size, and column density. Confirm the right-side page preview updates.
7. If no usable system or custom font is found, confirm the warning dialog.
8. Click `生成 PDF`.

## Expected Result

- The app shows a success message.
- The PDF is created in the chosen output folder, for example `output\sample-AncientBook.pdf`.
- If that PDF already exists, the app creates the next safe name, such as `output\sample-AncientBook-2.pdf`.
- The app accepts `.txt`, `.md`, `.docx`, selectable-text `.pdf`, `.rtf`, `.html`, and `.odt` documents.
- If a legacy `.doc` file is selected, the app asks the user to save it as `.docx` first.
- The PDF text is vertical.
- The page has an ancient-book-style background with paper texture and framed page styling.
- The desktop window has a left settings panel, right page preview, and bottom status area.
- The app does not upload text.
- No font files are bundled with the app by default.

## Manual Coverage

- [ ] Choose `素雅书页`, `朱栏格页`, and `旧藏纸页` at least once.
- [ ] Confirm the vermilion template has red ruled framing.
- [ ] Confirm the aged template has visible old-paper texture while the text remains readable.
- [ ] Generate once with an installed system font.
- [ ] Choose `Custom font file` and confirm browsing still works.
- [ ] Generate once from a `.docx` document.
- [ ] Select a legacy `.doc` file and confirm the app asks for `.docx`.
- [ ] Select a scanned or blank `.pdf` and confirm the app says OCR is not supported yet.
- [ ] Generate one A4 中字 标准 PDF.
- [ ] Generate one A5 大字 疏朗 PDF.
- [ ] Confirm the app warns if no usable system or custom font is available.
