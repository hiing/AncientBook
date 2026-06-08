from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ancientbook.document_reader import DocumentReadError, read_document_files
from ancientbook.layout import layout_tokens
from ancientbook.markup import parse_markup
from ancientbook.pdf import PdfGenerationError, write_pdf
from ancientbook.presets import DEFAULT_COLUMNS, DEFAULT_FONT_SIZE, DEFAULT_PAPER_SIZE, DEFAULT_TEMPLATE, build_layout_settings


class FriendlyGenerationError(ValueError):
    pass


@dataclass(frozen=True)
class GenerateRequest:
    text_files: list[Path]
    output_path: Path
    font_path: Path | None = None
    title: str = "AncientBook"
    overwrite: bool = False
    template_key: str = DEFAULT_TEMPLATE
    paper_size: str = DEFAULT_PAPER_SIZE
    font_size: str = DEFAULT_FONT_SIZE
    columns: str = DEFAULT_COLUMNS


@dataclass(frozen=True)
class GenerateResult:
    output_path: Path
    page_count: int


def _validate_request(request: GenerateRequest) -> None:
    if not request.text_files:
        raise FriendlyGenerationError("请选择至少一个文档文件。")
    for text_file in request.text_files:
        if not Path(text_file).exists():
            raise FriendlyGenerationError(f"找不到这个文档文件：{text_file}")
    if str(request.output_path).strip() in {"", "."}:
        raise FriendlyGenerationError("请选择 PDF 保存位置。")
    if request.output_path.suffix.lower() != ".pdf":
        raise FriendlyGenerationError("输出文件需要以 .pdf 结尾。")
    if request.output_path.parent and not request.output_path.parent.exists():
        raise FriendlyGenerationError("PDF 保存目录不存在。")
    if request.font_path is not None and not request.font_path.exists():
        raise FriendlyGenerationError(f"找不到这个字体文件：{request.font_path}")


def generate_pdf_from_request(request: GenerateRequest) -> GenerateResult:
    _validate_request(request)
    try:
        text = read_document_files(request.text_files)
        tokens = parse_markup(text)
        settings = build_layout_settings(request.paper_size, request.font_size, request.columns)
        placements = layout_tokens(tokens, settings)
        write_pdf(
            request.output_path,
            placements,
            settings,
            request.font_path,
            request.title,
            overwrite=request.overwrite,
            template_key=request.template_key,
        )
    except DocumentReadError as exc:
        raise FriendlyGenerationError(_friendly_document_error(exc)) from exc
    except PdfGenerationError as exc:
        message = str(exc)
        if "already exists" in message:
            raise FriendlyGenerationError("将覆盖已有 PDF。") from exc
        if "Font file" in message:
            raise FriendlyGenerationError("字体文件无法读取，请换一个字体。") from exc
        raise FriendlyGenerationError("生成失败，请换一个输出位置或检查文档文件后再试。") from exc
    except Exception as exc:
        raise FriendlyGenerationError("生成失败，请换一个输出位置或检查文档文件后再试。") from exc
    page_count = max((placement.page_index for placement in placements), default=0) + 1
    return GenerateResult(output_path=request.output_path, page_count=page_count)


def _friendly_document_error(error: DocumentReadError) -> str:
    message = str(error)
    if "Please save .doc as .docx" in message:
        return "请先把 .doc 另存为 .docx，再导入。"
    if "PDF has no selectable text" in message:
        return "这个 PDF 没有可复制文字，可能是扫描件；当前版本暂不支持 OCR。"
    if "Unsupported document format" in message:
        return "暂不支持这种文档格式。"
    if "Document must be UTF-8 text" in message:
        return "这个文本类文档无法按 UTF-8 读取，请另存为 UTF-8 后再试。"
    return "这个文档无法读取，请换一个文件或先另存为支持的格式。"
