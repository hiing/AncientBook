from pathlib import Path


def test_windows_build_script_exists_and_targets_desktop_app():
    script = Path("scripts/build_windows.ps1")
    entrypoint = Path("packaging/windows_desktop.py")
    icon = Path("assets/icon/AncientBook.ico")

    assert script.exists()
    assert entrypoint.exists()
    assert icon.exists()
    text = script.read_text(encoding="utf-8")
    assert "PyInstaller" in text
    assert "-m ancientbook.desktop.app" not in text
    assert "packaging/windows_desktop.py" in text
    assert "--name AncientBook" in text
    assert "--icon" in text
    assert '$IconPath = Join-Path $ProjectRoot "assets\\icon\\AncientBook.ico"' in text
    assert "--icon $IconPath" in text
    assert "--collect-all PySide6" not in text
    assert "--hidden-import PySide6.QtCore" in text
    assert "--hidden-import PySide6.QtGui" in text
    assert "--hidden-import PySide6.QtWidgets" in text
    assert "--exclude-module PySide6.QtWebEngineCore" in text

    entrypoint_text = entrypoint.read_text(encoding="utf-8")
    assert "ancientbook.desktop.app" in entrypoint_text


def test_windows_icon_assets_exist_and_are_multisize():
    icon = Path("assets/icon/AncientBook.ico")
    source = Path("assets/icon/AncientBook-icon.png")

    assert source.exists()
    assert icon.exists()
    assert source.stat().st_size > 1000
    assert icon.stat().st_size > 1000


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
        ".docx",
        ".pdf",
        ".doc",
        "output\\sample-AncientBook.pdf",
        "output\\sample-AncientBook-2.pdf",
        "assets\\icon\\AncientBook.ico",
        "does not upload text",
        "No font files are bundled",
    ]:
        assert phrase in guide_text or phrase in readme
    assert "docs/release-checklists/non-programmer-acceptance.md" in readme


def test_windows_release_package_script_creates_user_facing_zip():
    script = Path("scripts/package_windows_release.ps1")

    assert script.exists()
    text = script.read_text(encoding="utf-8")
    for phrase in [
        "scripts\\build_windows.ps1",
        "-SkipBuild",
        "AncientBook-Windows",
        "AncientBook-Windows.zip",
        "README-FIRST.txt",
        "THIRD_PARTY_NOTICES.md",
        "examples",
        "sample.txt",
        "Compress-Archive",
    ]:
        assert phrase in text

    readme = Path("README.md").read_text(encoding="utf-8")
    assert "scripts/package_windows_release.ps1" in readme
    assert "release\\AncientBook-Windows.zip" in readme
