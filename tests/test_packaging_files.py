from pathlib import Path


def test_windows_build_script_exists_and_targets_desktop_app():
    script = Path("scripts/build_windows.ps1")
    entrypoint = Path("packaging/windows_desktop.py")

    assert script.exists()
    assert entrypoint.exists()
    text = script.read_text(encoding="utf-8")
    assert "PyInstaller" in text
    assert "-m ancientbook.desktop.app" not in text
    assert "packaging/windows_desktop.py" in text
    assert "--name AncientBook" in text

    entrypoint_text = entrypoint.read_text(encoding="utf-8")
    assert "ancientbook.desktop.app" in entrypoint_text


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


def test_non_programmer_acceptance_docs_are_discoverable():
    guide = Path("docs/release-checklists/non-programmer-acceptance.md")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert guide.exists()
    guide_text = guide.read_text(encoding="utf-8")
    for phrase in [
        "dist\\AncientBook\\AncientBook.exe",
        "examples\\sample.txt",
        "output\\sample-from-desktop.pdf",
        "does not upload text",
        "No font files are bundled",
    ]:
        assert phrase in guide_text
    assert "docs/release-checklists/non-programmer-acceptance.md" in readme
