from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ancientbook.app_service import GenerateRequest, GenerateResult
from ancientbook.desktop.preview import create_preview_image, pixmap_from_image
from ancientbook.desktop.ui_fonts import apply_interface_font
from ancientbook.desktop.worker import GenerateWorker
from ancientbook.output_naming import default_output_path, unique_output_path
from ancientbook.presets import (
    COLUMN_DENSITY_CHOICES,
    FONT_SIZE_CHOICES,
    PAPER_SIZE_CHOICES,
    TEMPLATE_CHOICES,
    choice_label,
)
from ancientbook.settings import AppSettings, load_settings, save_settings
from ancientbook.system_fonts import CUSTOM_FONT_KEY, available_font_choices, default_font_choice, resolve_font_path


DOCUMENT_FILE_FILTER = (
    "Documents (*.txt *.text *.md *.markdown *.docx *.pdf *.rtf *.html *.htm *.odt *.doc);;"
    "All files (*.*)"
)


ANCIENTBOOK_STYLE = """
QMainWindow#AncientBookWindow {
    background: #eee4cd;
}
QWidget#CentralDesk {
    background: #eee4cd;
    color: #2b2118;
    font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans SC", "SimSun", "Segoe UI";
    font-size: 13px;
}
QLabel#SealLabel {
    background: #a83225;
    color: #fff8e8;
    border: 1px solid #7e211a;
    border-radius: 7px;
    font-size: 22px;
    font-weight: 700;
    min-width: 46px;
    min-height: 46px;
    max-width: 46px;
    max-height: 46px;
}
QLabel#BrandTitle {
    color: #2b2118;
    font-size: 28px;
    font-weight: 700;
}
QLabel#BrandSubtitle,
QLabel#PreviewMeta,
QLabel#StatusLabel {
    color: #695944;
}
QLabel#SectionTitle {
    color: #2b2118;
    font-size: 16px;
    font-weight: 700;
}
QFrame#ControlPanel,
QFrame#StatusPanel {
    background: #fff9ea;
    border: 1px solid #c7b47e;
    border-radius: 8px;
}
QFrame#PreviewPanel {
    background: #e4dcc5;
    border: 1px solid #9faa80;
    border-radius: 8px;
}
QLabel#PagePreview {
    background: #d8cfb8;
    border: 1px solid #a99463;
    border-radius: 8px;
    padding: 16px;
}
QLineEdit,
QComboBox {
    background: #fffdf4;
    color: #2b2118;
    border: 1px solid #c5aa72;
    border-radius: 6px;
    min-height: 30px;
    padding: 4px 8px;
}
QComboBox QAbstractItemView {
    background: #fffdf4;
    color: #2b2118;
    border: 1px solid #c5aa72;
    selection-background-color: #efe1bd;
    selection-color: #2b2118;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 4px 8px;
}
QLineEdit:focus,
QComboBox:focus {
    border: 1px solid #66724c;
}
QPushButton {
    background: #f8f0dc;
    color: #2b2118;
    border: 1px solid #b69a68;
    border-radius: 6px;
    min-height: 30px;
    padding: 5px 12px;
}
QPushButton:hover {
    background: #f1e1bc;
}
QPushButton#PrimaryButton {
    background: #a83225;
    color: #fff8e8;
    border: 1px solid #7e211a;
    border-radius: 6px;
    font-size: 15px;
    font-weight: 700;
    min-height: 42px;
}
QPushButton#PrimaryButton:hover {
    background: #8f271f;
}
QPushButton#PrimaryButton:disabled {
    background: #ad9580;
    color: #fff9ea;
}
"""


class PreviewPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("PreviewPanel")

        self.title_label = QLabel("版式预览")
        self.title_label.setObjectName("SectionTitle")
        self.page_label = QLabel()
        self.page_label.setObjectName("PagePreview")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setMinimumSize(300, 430)
        self.page_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.meta_label = QLabel("")
        self.meta_label.setObjectName("PreviewMeta")
        self.meta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addWidget(self.title_label)
        layout.addWidget(self.page_label, 1)
        layout.addWidget(self.meta_label)

    def update_preview(self, template_key: str, paper_size: str, font_size: str, columns: str) -> None:
        image = create_preview_image(template_key, paper_size, font_size, columns)
        self.page_label.setPixmap(pixmap_from_image(image))
        self.meta_label.setText(
            " · ".join(
                [
                    choice_label(template_key, TEMPLATE_CHOICES),
                    choice_label(paper_size, PAPER_SIZE_CHOICES),
                    choice_label(font_size, FONT_SIZE_CHOICES),
                    choice_label(columns, COLUMN_DENSITY_CHOICES),
                ]
            )
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("AncientBookWindow")
        self.setWindowTitle("AncientBook")
        apply_interface_font(self)
        self.setStyleSheet(ANCIENTBOOK_STYLE)
        self._settings = load_settings()
        self._thread: QThread | None = None
        self._worker: GenerateWorker | None = None

        self.text_files_edit = QLineEdit()
        self.output_edit = QLineEdit(self._settings.last_output_dir)
        self.font_edit = QLineEdit(self._settings.last_font_path)
        self._font_choices = available_font_choices()
        selected_font_key = self._settings.font_choice_key or default_font_choice()
        self.font_combo = self._font_combo_for_choices(self._font_choices, selected_font_key)
        self.template_combo = self._combo_for_choices(TEMPLATE_CHOICES, self._settings.template_key)
        self.paper_size_combo = self._combo_for_choices(PAPER_SIZE_CHOICES, self._settings.paper_size)
        self.font_size_combo = self._combo_for_choices(FONT_SIZE_CHOICES, self._settings.font_size)
        self.columns_combo = self._combo_for_choices(COLUMN_DENSITY_CHOICES, self._settings.columns)
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("StatusLabel")
        self.generate_button = QPushButton("生成 PDF")
        self.generate_button.setObjectName("PrimaryButton")
        self.preview_panel = PreviewPanel()

        self._build_ui()
        for combo in (self.template_combo, self.paper_size_combo, self.font_size_combo, self.columns_combo):
            combo.currentIndexChanged.connect(self._refresh_preview)
        self._refresh_preview()
        self.generate_button.clicked.connect(self.generate_pdf)

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("CentralDesk")
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 18)
        root.setSpacing(16)

        header = QHBoxLayout()
        seal_label = QLabel("古")
        seal_label.setObjectName("SealLabel")
        seal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_stack = QVBoxLayout()
        title_stack.setSpacing(2)
        title = QLabel("AncientBook")
        title.setObjectName("BrandTitle")
        subtitle = QLabel("古籍排版")
        subtitle.setObjectName("BrandSubtitle")
        title_stack.addWidget(title)
        title_stack.addWidget(subtitle)
        header.addWidget(seal_label)
        header.addLayout(title_stack)
        header.addStretch(1)

        content = QHBoxLayout()
        content.setSpacing(18)

        self.control_panel = QFrame()
        self.control_panel.setObjectName("ControlPanel")
        self.control_panel.setMinimumWidth(430)
        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(18, 18, 18, 18)
        control_layout.setSpacing(14)

        section_title = QLabel("排版设置")
        section_title.setObjectName("SectionTitle")
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)

        form.addRow("文档", self._with_button(self.text_files_edit, "选择", self.choose_text_files))
        form.addRow("输出文件夹", self._with_button(self.output_edit, "选择", self.choose_output_folder))
        form.addRow("字体", self.font_combo)
        form.addRow("自选字体", self._with_button(self.font_edit, "选择", self.choose_font_file))
        form.addRow("页面模板", self.template_combo)
        form.addRow("纸张", self.paper_size_combo)
        form.addRow("字号", self.font_size_combo)
        form.addRow("栏数", self.columns_combo)

        control_layout.addWidget(section_title)
        control_layout.addLayout(form)
        control_layout.addStretch(1)
        control_layout.addWidget(self.generate_button)

        content.addWidget(self.control_panel, 0)
        content.addWidget(self.preview_panel, 1)

        status_panel = QFrame()
        status_panel.setObjectName("StatusPanel")
        status_layout = QHBoxLayout(status_panel)
        status_layout.setContentsMargins(14, 9, 14, 9)
        status_layout.addWidget(self.status_label, 1)

        root.addLayout(header)
        root.addLayout(content, 1)
        root.addWidget(status_panel)
        self.setCentralWidget(central)
        self.resize(980, 620)

    def _with_button(self, line_edit: QLineEdit, label: str, callback: Callable[[], None]) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        button = QPushButton(label)
        button.setObjectName("SecondaryButton")
        button.clicked.connect(callback)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        return widget

    def _combo_for_choices(self, choices, selected_key: str) -> QComboBox:
        combo = QComboBox()
        for choice in choices:
            combo.addItem(choice.label, choice.key)
        index = combo.findData(selected_key)
        combo.setCurrentIndex(index if index >= 0 else 0)
        combo.currentIndexChanged.connect(self._save_choice_settings)
        self._apply_combo_font(combo)
        return combo

    def _font_combo_for_choices(self, choices, selected_key: str) -> QComboBox:
        combo = QComboBox()
        for choice in choices:
            combo.addItem(choice.label, choice.key)
        index = combo.findData(selected_key)
        combo.setCurrentIndex(index if index >= 0 else 0)
        combo.currentIndexChanged.connect(self._save_choice_settings)
        self._apply_combo_font(combo)
        return combo

    def _apply_combo_font(self, combo: QComboBox) -> None:
        apply_interface_font(combo)
        apply_interface_font(combo.view())

    def _selected_key(self, combo: QComboBox) -> str:
        value = combo.currentData()
        return str(value) if value is not None else ""

    def _refresh_preview(self, *_args: object) -> None:
        self.preview_panel.update_preview(
            self._selected_key(self.template_combo),
            self._selected_key(self.paper_size_combo),
            self._selected_key(self.font_size_combo),
            self._selected_key(self.columns_combo),
        )

    def _resolved_font_path(self) -> Path | None:
        font_text = self.font_edit.text().strip()
        custom_path = Path(font_text) if font_text else None
        return resolve_font_path(self._selected_key(self.font_combo), custom_path)

    def _save_choice_settings(self, *_args: object) -> None:
        if not all(
            hasattr(self, name)
            for name in ("font_combo", "template_combo", "paper_size_combo", "font_size_combo", "columns_combo")
        ):
            return
        self._settings = AppSettings(
            last_text_dir=self._settings.last_text_dir,
            last_output_dir=self._settings.last_output_dir,
            last_font_path=self.font_edit.text().strip(),
            font_choice_key=self._selected_key(self.font_combo),
            template_key=self._selected_key(self.template_combo),
            paper_size=self._selected_key(self.paper_size_combo),
            font_size=self._selected_key(self.font_size_combo),
            columns=self._selected_key(self.columns_combo),
        )
        save_settings(None, self._settings)

    def choose_text_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select documents",
            self._settings.last_text_dir,
            DOCUMENT_FILE_FILTER,
        )
        if files:
            self.text_files_edit.setText(";".join(files))
            output_dir = self._settings.last_output_dir or str(Path(files[0]).parent)
            if not self.output_edit.text().strip():
                self.output_edit.setText(output_dir)
            self._settings = AppSettings(
                last_text_dir=str(Path(files[0]).parent),
                last_output_dir=output_dir,
                last_font_path=self._settings.last_font_path,
                font_choice_key=self._settings.font_choice_key,
                template_key=self._settings.template_key,
                paper_size=self._settings.paper_size,
                font_size=self._settings.font_size,
                columns=self._settings.columns,
            )
            save_settings(None, self._settings)

    def choose_output_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Choose output folder",
            self._settings.last_output_dir,
        )
        if path:
            self.output_edit.setText(path)
            self._settings = AppSettings(
                last_text_dir=self._settings.last_text_dir,
                last_output_dir=path,
                last_font_path=self._settings.last_font_path,
                font_choice_key=self._settings.font_choice_key,
                template_key=self._settings.template_key,
                paper_size=self._settings.paper_size,
                font_size=self._settings.font_size,
                columns=self._settings.columns,
            )
            save_settings(None, self._settings)

    def choose_output_file(self) -> None:
        self.choose_output_folder()

    def choose_font_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose font file",
            self._settings.last_font_path,
            "Font files (*.ttf *.otf);;All files (*.*)",
        )
        if path:
            self.font_edit.setText(path)
            index = self.font_combo.findData(CUSTOM_FONT_KEY)
            if index >= 0:
                self.font_combo.setCurrentIndex(index)
            self._settings = AppSettings(
                last_text_dir=self._settings.last_text_dir,
                last_output_dir=self._settings.last_output_dir,
                last_font_path=path,
                font_choice_key=self._selected_key(self.font_combo),
                template_key=self._settings.template_key,
                paper_size=self._settings.paper_size,
                font_size=self._settings.font_size,
                columns=self._settings.columns,
            )
            save_settings(None, self._settings)

    def _build_request(self) -> GenerateRequest:
        text_files = [Path(part) for part in self.text_files_edit.text().split(";") if part.strip()]
        output_text = self.output_edit.text().strip()
        output_path = unique_output_path(default_output_path(text_files, Path(output_text) if output_text else None))
        return GenerateRequest(
            text_files=text_files,
            output_path=output_path,
            font_path=self._resolved_font_path(),
            overwrite=False,
            template_key=self._selected_key(self.template_combo),
            paper_size=self._selected_key(self.paper_size_combo),
            font_size=self._selected_key(self.font_size_combo),
            columns=self._selected_key(self.columns_combo),
        )

    def generate_pdf(self) -> None:
        self._save_choice_settings()
        request = self._build_request()
        if request.font_path is None:
            reply = QMessageBox.warning(
                self,
                "AncientBook",
                "未找到可用中文字体，中文字符可能显示不完整。仍要继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply != QMessageBox.Yes:
                return
        self.generate_button.setEnabled(False)
        self.status_label.setText("生成中...")

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
        self.status_label.setText(f"已生成：{result.output_path}")
        QMessageBox.information(self, "AncientBook", f"PDF generated:\n{result.output_path}")

    def _on_generation_failed(self, message: str) -> None:
        self.generate_button.setEnabled(True)
        self.status_label.setText("生成失败")
        QMessageBox.critical(self, "AncientBook", message)
