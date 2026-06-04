from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ancientbook.app_service import GenerateRequest, GenerateResult, generate_pdf_from_request


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
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
