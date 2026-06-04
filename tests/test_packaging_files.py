from pathlib import Path


def test_windows_build_script_exists_and_targets_desktop_app():
    script = Path("scripts/build_windows.ps1")

    assert script.exists()
    text = script.read_text(encoding="utf-8")
    assert "PyInstaller" in text
    assert "ancientbook.desktop.app" in text
    assert "--name AncientBook" in text


def test_pyinstaller_is_dev_dependency():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert '"pyinstaller>=6.10"' in pyproject


def test_third_party_notices_cover_packaged_dependencies():
    notice = Path("docs/licenses/THIRD_PARTY_NOTICES.md")

    assert notice.exists()
    text = notice.read_text(encoding="utf-8")
    for name in ["PySide6", "Pillow", "ReportLab", "pypdf", "PyInstaller"]:
        assert name in text
    assert "Fonts are not bundled" in text
