from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ancientbook.app_service import GenerateRequest, GenerateResult
from ancientbook.desktop.worker import GenerateWorker
from ancientbook.settings import AppSettings, load_settings, save_settings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AncientBook")
        self._settings = load_settings()
        self._thread: QThread | None = None
        self._worker: GenerateWorker | None = None

        self.text_files_edit = QLineEdit()
        self.output_edit = QLineEdit()
        self.font_edit = QLineEdit(self._settings.last_font_path)
        self.status_label = QLabel("Ready")
        self.generate_button = QPushButton("Generate PDF")

        self._build_ui()
        self.generate_button.clicked.connect(self.generate_pdf)

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        form = QFormLayout()

        form.addRow("Text files", self._with_button(self.text_files_edit, "Browse", self.choose_text_files))
        form.addRow("Output PDF", self._with_button(self.output_edit, "Browse", self.choose_output_file))
        form.addRow("Font file", self._with_button(self.font_edit, "Browse", self.choose_font_file))

        root.addLayout(form)
        root.addWidget(self.generate_button)
        root.addWidget(self.status_label)
        self.setCentralWidget(central)
        self.resize(720, 240)

    def _with_button(self, line_edit: QLineEdit, label: str, callback: Callable[[], None]) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        button = QPushButton(label)
        button.clicked.connect(callback)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        return widget

    def choose_text_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select text files",
            self._settings.last_text_dir,
            "Text files (*.txt);;All files (*.*)",
        )
        if files:
            self.text_files_edit.setText(";".join(files))
            self._settings = AppSettings(
                last_text_dir=str(Path(files[0]).parent),
                last_output_dir=self._settings.last_output_dir,
                last_font_path=self._settings.last_font_path,
            )
            save_settings(None, self._settings)

    def choose_output_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose output PDF",
            self._settings.last_output_dir,
            "PDF files (*.pdf)",
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path = f"{path}.pdf"
            self.output_edit.setText(path)
            self._settings = AppSettings(
                last_text_dir=self._settings.last_text_dir,
                last_output_dir=str(Path(path).parent),
                last_font_path=self._settings.last_font_path,
            )
            save_settings(None, self._settings)

    def choose_font_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose font file",
            self._settings.last_font_path,
            "Font files (*.ttf *.otf);;All files (*.*)",
        )
        if path:
            self.font_edit.setText(path)
            self._settings = AppSettings(
                last_text_dir=self._settings.last_text_dir,
                last_output_dir=self._settings.last_output_dir,
                last_font_path=path,
            )
            save_settings(None, self._settings)

    def _build_request(self) -> GenerateRequest:
        text_files = [Path(part) for part in self.text_files_edit.text().split(";") if part.strip()]
        output_path = Path(self.output_edit.text().strip())
        font_text = self.font_edit.text().strip()
        return GenerateRequest(
            text_files=text_files,
            output_path=output_path,
            font_path=Path(font_text) if font_text else None,
            overwrite=True,
        )

    def generate_pdf(self) -> None:
        request = self._build_request()
        self.generate_button.setEnabled(False)
        self.status_label.setText("Generating...")

        self._thread = QThread()
        self._worker = GenerateWorker(request)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.failed.connect(self._on_generation_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_generation_finished(self, result: GenerateResult) -> None:
        self.generate_button.setEnabled(True)
        self.status_label.setText(f"Generated: {result.output_path}")
        QMessageBox.information(self, "AncientBook", f"PDF generated:\n{result.output_path}")

    def _on_generation_failed(self, message: str) -> None:
        self.generate_button.setEnabled(True)
        self.status_label.setText("Generation failed")
        QMessageBox.critical(self, "AncientBook", message)
