from ancientbook.markup import parse_markup
from ancientbook.model import TokenKind


def kinds_and_values(text: str):
    return [(token.kind, token.value) for token in parse_markup(text)]


def test_parse_text_comment_and_blank():
    assert kinds_and_values("天地【注】@玄") == [
        (TokenKind.TEXT, "天"),
        (TokenKind.TEXT, "地"),
        (TokenKind.COMMENT, "注"),
        (TokenKind.BLANK, " "),
        (TokenKind.TEXT, "玄"),
    ]


def test_parse_page_and_column_breaks():
    assert kinds_and_values("天%地$玄") == [
        (TokenKind.TEXT, "天"),
        (TokenKind.PAGE_BREAK, ""),
        (TokenKind.TEXT, "地"),
        (TokenKind.COLUMN_BREAK, ""),
        (TokenKind.TEXT, "玄"),
    ]


def test_unclosed_comment_is_preserved_as_text():
    assert kinds_and_values("天地【未完") == [
        (TokenKind.TEXT, "天"),
        (TokenKind.TEXT, "地"),
        (TokenKind.TEXT, "【"),
        (TokenKind.TEXT, "未"),
        (TokenKind.TEXT, "完"),
    ]


def test_normalize_punctuation_to_period():
    assert kinds_and_values("天，地！") == [
        (TokenKind.TEXT, "天"),
        (TokenKind.TEXT, "。"),
        (TokenKind.TEXT, "地"),
        (TokenKind.TEXT, "。"),
    ]
