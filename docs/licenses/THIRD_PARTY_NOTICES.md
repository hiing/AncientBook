# Third-Party Notices

AncientBook is a clean-room Python implementation. It does not copy vRain source code.

AncientBook's own source code is released under the MIT License. Third-party
libraries, packaging tools, and user-selected fonts keep their own licenses.

Packaged runtime dependencies may include:

- PySide6: Qt for Python bindings. Review Qt for Python licensing before public redistribution.
- Pillow: Python Imaging Library fork.
- ReportLab: PDF generation library.
- pypdf: PDF inspection and manipulation library used in tests.
- PyInstaller: packaging tool used to build the Windows app.

Fonts are not bundled by default. Users choose local fonts installed on their own machine or font files they have the right to use.

Before publishing a public release, review the exact installed package versions and their license files from the build environment.
