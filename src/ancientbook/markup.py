from __future__ import annotations

from ancientbook.model import Token, TokenKind


PUNCTUATION_TO_PERIOD = {
    "，",
    "、",
    "；",
    "：",
    "！",
    "？",
    ",",
    ";",
    ":",
    "!",
    "?",
}


def _normalize_char(ch: str) -> str:
    if ch in PUNCTUATION_TO_PERIOD:
        return "。"
    return ch


def parse_markup(text: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "【":
            end = text.find("】", i + 1)
            if end == -1:
                tokens.append(Token(TokenKind.TEXT, ch))
                i += 1
                continue
            tokens.append(Token(TokenKind.COMMENT, text[i + 1 : end]))
            i = end + 1
            continue
        if ch == "%":
            tokens.append(Token(TokenKind.PAGE_BREAK))
            i += 1
            continue
        if ch == "$":
            tokens.append(Token(TokenKind.COLUMN_BREAK))
            i += 1
            continue
        if ch == "@":
            tokens.append(Token(TokenKind.BLANK, " "))
            i += 1
            continue
        if ch in {"\r", "\n", "\t"}:
            i += 1
            continue
        tokens.append(Token(TokenKind.TEXT, _normalize_char(ch)))
        i += 1
    return tokens
