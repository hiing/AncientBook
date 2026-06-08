from __future__ import annotations

from functools import lru_cache

from PySide6.QtGui import QFont, QFontDatabase

from ancientbook.system_fonts import available_font_choices


PREFERRED_INTERFACE_FAMILIES = (
    "Microsoft YaHei",
    "Microsoft YaHei UI",
    "Noto Sans SC",
    "SimSun",
    "NSimSun",
)


@lru_cache(maxsize=1)
def preferred_interface_font_family() -> str | None:
    for choice in available_font_choices():
        if choice.path is None:
            continue
        font_id = QFontDatabase.addApplicationFont(str(choice.path))
        if font_id < 0:
            continue
        families = QFontDatabase.applicationFontFamilies(font_id)
        for preferred in PREFERRED_INTERFACE_FAMILIES:
            if preferred in families:
                return preferred
        if families:
            return families[0]

    available = set(QFontDatabase.families())
    for family in PREFERRED_INTERFACE_FAMILIES:
        if family in available:
            return family
    return None


def apply_interface_font(target, point_size: int = 10) -> None:
    family = preferred_interface_font_family()
    if family:
        target.setFont(QFont(family, point_size))
