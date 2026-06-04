from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ancientbook.app_service import FriendlyGenerationError, GenerateRequest, GenerateResult, generate_pdf_from_request


class GenerateWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, request: GenerateRequest):
        super().__init__()
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            result: GenerateResult = generate_pdf_from_request(self._request)
        except FriendlyGenerationError as exc:
            self.failed.emit(str(exc))
            return
        except Exception:
            self.failed.emit("生成失败，请换一个输出位置或检查文本文件后再试。")
            return
        self.finished.emit(result)
