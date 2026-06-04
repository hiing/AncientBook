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


def test_desktop_app_imports():
    from ancientbook.desktop.app import main

    assert main is not None
