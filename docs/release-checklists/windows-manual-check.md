# Windows Manual Release Check

Use this checklist after building `dist\AncientBook\AncientBook.exe`.

- [ ] Launch `dist\AncientBook\AncientBook.exe`.
- [ ] Select one or more UTF-8 `.txt` files, such as `examples\sample.txt`.
- [ ] Select an output `.pdf` path, such as `output\sample-from-desktop.pdf`.
- [ ] Optionally select a local `.ttf` or `.otf` font.
- [ ] Choose each template at least once.
- [ ] Generate one A4 Medium Standard PDF.
- [ ] Generate one A5 Large Fewer PDF.
- [ ] Confirm the app warns when no font is selected.
- [ ] Click Generate PDF.
- [ ] Confirm the app shows a success message.
- [ ] Open the generated PDF.
- [ ] Confirm the text is vertical and the page has an ancient-book-style background.
- [ ] Confirm no bundled font files were added to the repository.
