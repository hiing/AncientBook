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
