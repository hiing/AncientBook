from __future__ import annotations

import html as html_lib
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from zipfile import BadZipFile, ZipFile

from pypdf import PdfReader


SUPPORTED_DOCUMENT_EXTENSIONS = (
    ".txt",
    ".text",
    ".md",
    ".markdown",
    ".docx",
    ".pdf",
    ".rtf",
    ".html",
    ".htm",
    ".odt",
)


class DocumentReadError(RuntimeError):
    pass


def read_document_files(paths: Iterable[Path]) -> str:
    chunks: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        text = _read_document(path)
        cleaned = _normalize_text(_clean_control_characters(text))
        if cleaned:
            chunks.append(cleaned)
    return "\n".join(chunks)


def _read_document(path: Path) -> str:
    if not path.exists():
        raise DocumentReadError(f"Cannot read document: {path}")

    suffix = path.suffix.lower()
    if suffix in {".txt", ".text"}:
        return _read_utf8_text(path)
    if suffix in {".md", ".markdown"}:
        return _markdown_to_text(_read_utf8_text(path))
    if suffix == ".docx":
        return _docx_to_text(path)
    if suffix == ".pdf":
        return _pdf_to_text(path)
    if suffix == ".rtf":
        return _rtf_to_text(_read_utf8_text(path))
    if suffix in {".html", ".htm"}:
        return _html_to_text(_read_utf8_text(path))
    if suffix == ".odt":
        return _odt_to_text(path)
    if suffix == ".doc":
        raise DocumentReadError("Please save .doc as .docx before importing.")
    raise DocumentReadError(f"Unsupported document format: {path.suffix}")


def _read_utf8_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DocumentReadError(f"Cannot read document: {path}") from exc
    except UnicodeDecodeError as exc:
        raise DocumentReadError(f"Document must be UTF-8 text: {path}") from exc


def _docx_to_text(path: Path) -> str:
    try:
        with ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except (OSError, BadZipFile, KeyError) as exc:
        raise DocumentReadError(f"Cannot read DOCX document: {path}") from exc

    return _wordprocessing_xml_to_text(xml, path)


def _wordprocessing_xml_to_text(xml: bytes, path: Path) -> str:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise DocumentReadError(f"Cannot parse DOCX document: {path}") from exc

    chunks: list[str] = []

    def walk(element: ET.Element) -> None:
        name = _local_name(element.tag)
        if name == "t" and element.text:
            chunks.append(element.text)
        elif name == "tab":
            chunks.append("\t")
        elif name in {"br", "cr"}:
            chunks.append("\n")

        for child in element:
            walk(child)

        if name == "p":
            chunks.append("\n")

    walk(root)
    return "".join(chunks)


def _pdf_to_text(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:
                raise DocumentReadError(f"Cannot read encrypted PDF: {path}") from exc
        pages = [page.extract_text() or "" for page in reader.pages]
    except DocumentReadError:
        raise
    except Exception as exc:
        raise DocumentReadError(f"Cannot read PDF document: {path}") from exc

    text = "\n".join(pages)
    if not _normalize_text(text):
        raise DocumentReadError(f"PDF has no selectable text: {path}")
    return text


def _odt_to_text(path: Path) -> str:
    try:
        with ZipFile(path) as archive:
            xml = archive.read("content.xml")
    except (OSError, BadZipFile, KeyError) as exc:
        raise DocumentReadError(f"Cannot read ODT document: {path}") from exc

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise DocumentReadError(f"Cannot parse ODT document: {path}") from exc

    chunks: list[str] = []

    def walk(element: ET.Element) -> None:
        name = _local_name(element.tag)
        if element.text:
            chunks.append(element.text)

        if name == "tab":
            chunks.append("\t")
        elif name == "line-break":
            chunks.append("\n")
        elif name == "s":
            count = int(element.attrib.get("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}c", "1"))
            chunks.append(" " * count)

        for child in element:
            walk(child)
            if child.tail:
                chunks.append(child.tail)

        if name in {"p", "h"}:
            chunks.append("\n")

    walk(root)
    return "".join(chunks)


def _markdown_to_text(text: str) -> str:
    text = re.sub(r"```.*?```", lambda match: match.group(0).replace("```", ""), text, flags=re.DOTALL)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    lines: list[str] = []
    for line in text.splitlines():
        line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
        line = re.sub(r"^\s{0,3}>\s?", "", line)
        line = re.sub(r"^\s*[-*+]\s+", "", line)
        line = re.sub(r"^\s*\d+[.)]\s+", "", line)
        line = line.replace("`", "")
        line = re.sub(r"[*_~]{1,3}", "", line)
        lines.append(line)
    return "\n".join(lines)


def _rtf_to_text(text: str) -> str:
    def replace_unicode(match: re.Match[str]) -> str:
        value = int(match.group(1))
        if value < 0:
            value += 65536
        return chr(value)

    text = re.sub(r"\\u(-?\d+)\??", replace_unicode, text)
    text = re.sub(r"\\(?:par|line)\b ?", "\n", text)
    text = re.sub(r"\\tab\b ?", "\t", text)
    text = re.sub(r"\\'([0-9a-fA-F]{2})", lambda match: bytes.fromhex(match.group(1)).decode("cp1252"), text)
    text = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", text)
    text = re.sub(r"\\([{}\\])", r"\1", text)
    return text.replace("{", "").replace("}", "")


def _html_to_text(text: str) -> str:
    parser = _TextHTMLParser()
    parser.feed(text)
    parser.close()
    return parser.text


class _TextHTMLParser(HTMLParser):
    _BLOCK_TAGS = {"p", "div", "section", "article", "header", "footer", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    @property
    def text(self) -> str:
        return "".join(self._chunks)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._BLOCK_TAGS or tag == "br":
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        self._chunks.append(html_lib.unescape(data))


def _clean_control_characters(text: str) -> str:
    allowed = {"\n", "\r", "\t"}
    return "".join(ch for ch in text if ch in allowed or ord(ch) >= 32)


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(line.split()) if "\t" not in line else line.strip() for line in normalized.split("\n")]
    return "\n".join(line for line in lines if line)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag
