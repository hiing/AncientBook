def test_desktop_package_imports():
    import ancientbook.desktop

    assert ancientbook.desktop is not None


def test_worker_imports():
    from ancientbook.desktop.worker import GenerateWorker

    assert GenerateWorker is not None
