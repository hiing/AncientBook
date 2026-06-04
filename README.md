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
