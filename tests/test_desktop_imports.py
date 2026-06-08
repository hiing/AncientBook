def test_desktop_package_imports():
    import ancientbook.desktop

    assert ancientbook.desktop is not None


def test_worker_imports():
    from ancientbook.desktop.worker import GenerateWorker

    assert GenerateWorker is not None


def test_main_window_imports():
    from ancientbook.desktop.main_window import MainWindow

    assert MainWindow is not None


def test_main_window_has_usability_choice_helpers():
    from ancientbook.desktop.main_window import MainWindow

    assert hasattr(MainWindow, "_combo_for_choices")
    assert hasattr(MainWindow, "_save_choice_settings")


def test_main_window_has_system_font_choice_helpers():
    from ancientbook.desktop.main_window import MainWindow

    assert hasattr(MainWindow, "_font_combo_for_choices")
    assert hasattr(MainWindow, "_resolved_font_path")


def test_main_window_has_output_folder_helper():
    from ancientbook.desktop.main_window import MainWindow

    assert hasattr(MainWindow, "choose_output_folder")


def test_main_window_document_file_filter_lists_supported_formats():
    from ancientbook.desktop.main_window import DOCUMENT_FILE_FILTER

    for extension in ["*.txt", "*.md", "*.docx", "*.pdf", "*.rtf", "*.html", "*.odt", "*.doc"]:
        assert extension in DOCUMENT_FILE_FILTER


def test_main_window_build_request_avoids_overwriting_existing_pdf(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication

    from ancientbook import settings
    from ancientbook.desktop.main_window import MainWindow

    monkeypatch.setattr(settings, "default_settings_path", lambda: tmp_path / "settings.json")
    app = QApplication.instance() or QApplication([])
    text_file = tmp_path / "sample.txt"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    text_file.write_text("sample", encoding="utf-8")
    (output_dir / "sample-AncientBook.pdf").write_bytes(b"%PDF existing")

    window = MainWindow()
    window.text_files_edit.setText(str(text_file))
    window.output_edit.setText(str(output_dir))

    request = window._build_request()

    assert request.output_path == output_dir / "sample-AncientBook-2.pdf"
    assert request.overwrite is False
    window.close()
    assert app is not None


def test_main_window_uses_book_desk_layout(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication

    from ancientbook import settings
    from ancientbook.desktop.main_window import MainWindow

    monkeypatch.setattr(settings, "default_settings_path", lambda: tmp_path / "settings.json")
    app = QApplication.instance() or QApplication([])

    window = MainWindow()

    assert window.objectName() == "AncientBookWindow"
    assert window.control_panel.objectName() == "ControlPanel"
    assert window.preview_panel.objectName() == "PreviewPanel"
    assert window.generate_button.objectName() == "PrimaryButton"
    assert "QFrame#PreviewPanel" in window.styleSheet()
    assert window.preview_panel.page_label.pixmap() is not None
    assert not window.preview_panel.page_label.pixmap().isNull()
    window.close()
    assert app is not None


def test_desktop_ui_loads_system_chinese_interface_font():
    from PySide6.QtWidgets import QApplication

    from ancientbook.desktop.ui_fonts import preferred_interface_font_family

    app = QApplication.instance() or QApplication([])
    family = preferred_interface_font_family()

    assert family in {"Microsoft YaHei", "Microsoft YaHei UI", "SimSun", "NSimSun", "Noto Sans SC"}
    assert app is not None


def test_main_window_font_combo_uses_readable_labels_and_interface_font(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication

    from ancientbook import settings
    from ancientbook.desktop.main_window import MainWindow
    from ancientbook.desktop.ui_fonts import preferred_interface_font_family

    monkeypatch.setattr(settings, "default_settings_path", lambda: tmp_path / "settings.json")
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    expected_family = preferred_interface_font_family()

    item_texts = [window.font_combo.itemText(index) for index in range(window.font_combo.count())]

    assert all(text.strip() for text in item_texts)
    assert any(" / " in text for text in item_texts)
    assert any("Microsoft YaHei" in text or "SimSun" in text for text in item_texts)
    assert window.font_combo.font().family() == expected_family
    assert window.font_combo.view().font().family() == expected_family
    window.close()
    assert app is not None


def test_desktop_app_imports():
    from ancientbook.desktop.app import main

    assert main is not None
