# AncientBook Next UI Plan Notes

The next plan should build the PySide6 desktop interface on top of the tested core pipeline.

Recommended next tasks:

1. Add an application service function that accepts input paths, output path, optional font path, title, and overwrite flag.
2. Add a PySide6 main window with file pickers and a Generate button.
3. Run PDF generation in a worker thread so the UI stays responsive.
4. Show friendly errors for unreadable text files, missing fonts, and existing output files.
5. Save last-used paths in JSON settings.
6. Add a basic Windows packaging plan with PyInstaller.
