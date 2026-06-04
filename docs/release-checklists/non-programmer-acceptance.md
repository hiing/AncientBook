# Non-Programmer Acceptance Check

This check is for a person who receives a built `dist\AncientBook` folder and does not need to know Python.

## First Run

1. Open `dist\AncientBook\AncientBook.exe`.
2. Click Browse beside Text files and choose `examples\sample.txt`.
3. Click Browse beside Output PDF and choose `output\sample-from-desktop.pdf`.
4. Leave Font file empty for the first run, or choose a local `.ttf` or `.otf` font you have the right to use.
5. Click Generate PDF.

## Expected Result

- The app shows a success message.
- The PDF is created at the chosen output path.
- The PDF text is vertical.
- The page has an ancient-book-style background.
- The app does not upload text.
- No font files are bundled with the app by default.
