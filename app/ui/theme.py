# -*- coding: utf-8 -*-
"""
Single source of truth for the Raionn desktop look.

The palette follows Apple's macOS/iOS light appearance — neutral greys for
every surface, hairline separators, near-black label text — with the Raionn
green kept as the one accent colour.  Every UI module imports its colour
tokens from here, so re-skinning the whole app means editing this file only.

Nothing here touches layout: no sizes, margins or widget arrangement.
"""
from PyQt5 import QtGui

# ── Accent (Raionn green, cleaned up) ────────────────────────────────────────
G50  = "#F1F8F4"   # faintest accent wash
G100 = "#D8EFE2"   # light accent fill / selection
G200 = "#5FB08A"   # mid accent — hover, scrollbar handles, rules
G400 = "#1F7A4D"   # PRIMARY accent — buttons, table headers
G600 = "#145C39"   # accent pressed
G800 = "#0B3A24"   # deepest accent

# ── Apple system neutrals (light appearance) ─────────────────────────────────
SURFACE = "#FFFFFF"   # cards, sheets, table bodies
BG      = "#F2F2F7"   # window background (systemGray6)
TEXT    = "#1D1D1F"   # label
MUTED   = "#6E6E73"   # secondaryLabel
SUBTLE  = "#8E8E93"   # tertiaryLabel
BORDER  = "#D8DADE"   # separator hairline
GRID    = "#E5E5EA"   # table gridlines (systemGray5) — lighter than a border
BG_2    = "#EBEBF0"   # one step down from BG — footers, hover fills

# ── Window chrome (dark graphite-green, like a pro macOS app) ────────────────
HEADER_BG  = "#243A2E"   # title bars
SIDEBAR_BG = "#1C2B23"   # sidebars / file lists

# ── Semantic ─────────────────────────────────────────────────────────────────
BLUE    = "#0071E3"   # Apple accent blue (secondary actions)
BLUE_HI = "#0062C4"
RED     = "#D70015"   # destructive
RED_HI  = "#B3000F"
RED_BG  = "#FFF1F0"   # destructive tint
AMBER   = "#B25000"

# ── Typography ───────────────────────────────────────────────────────────────
# Qt accepts a comma-separated family list in stylesheets and falls back to the
# first family that exists, so SF Pro is used on machines that have it and
# Windows 11's Segoe UI Variable (its closest counterpart) everywhere else.
FONT         = "'SF Pro Text', '.AppleSystemUIFont', 'Segoe UI Variable Text', 'Segoe UI'"
FONT_DISPLAY = "'SF Pro Display', '.AppleSystemUIFont', 'Segoe UI Variable Display', 'Segoe UI'"

# Monochrome symbol font — the Windows counterpart to SF Symbols.  Used instead
# of colour emoji, which look out of place next to flat UI chrome.
FONT_ICON    = "'SF Pro Display', 'Segoe Fluent Icons', 'Segoe MDL2 Assets'"


class Icon:
    """Segoe Fluent Icons code points, named for what they mean here."""
    LOCK     = ""
    KEY      = ""
    SHIELD   = ""
    PERSON   = ""
    MAIL     = ""
    EYE_SHOW = ""
    EYE_HIDE = ""
    CLOSE    = ""
    CHECK    = ""
    BACK     = ""
    DOCUMENT = ""
    DELETE   = ""
    REFRESH  = ""
    SAVE     = ""
    PRINT    = ""
    PDF      = ""
    OPEN     = ""
    ZOOM_IN  = ""
    ZOOM_OUT = ""

_PREFERRED_FAMILIES = (
    "SF Pro Text", "SF Pro Display", "Inter",
    "Segoe UI Variable Text", "Segoe UI", "Arial",
)
_resolved_family = None


def ui_font_family() -> str:
    """
    Best available single family name, for the QFont(...) constructor — which,
    unlike a stylesheet, takes one family rather than a fallback list.

    Resolved lazily and cached: QFontDatabase needs a live QApplication.
    """
    global _resolved_family
    if _resolved_family is None:
        try:
            available = set(QtGui.QFontDatabase().families())
            _resolved_family = next(
                (f for f in _PREFERRED_FAMILIES if f in available), "Segoe UI")
        except Exception:
            _resolved_family = "Segoe UI"
    return _resolved_family


def ui_font(point_size: int = 10, weight: int = QtGui.QFont.Normal) -> QtGui.QFont:
    """A QFont in the app's typeface."""
    return QtGui.QFont(ui_font_family(), point_size, weight)


# ── Shared control styles ────────────────────────────────────────────────────
# Message boxes, dialogs and menus created by Qt itself (QMessageBox,
# QFileDialog) are styled through this, applied once on the QApplication.
APP_STYLESHEET = f"""
QWidget {{
    font: 10pt {FONT};
    color: {TEXT};
}}
QToolTip {{
    background: {HEADER_BG}; color: #FFFFFF;
    border: none; border-radius: 6px;
    padding: 6px 9px; font: 9pt {FONT};
}}
QMessageBox, QDialog#QFileDialog, QFileDialog {{
    background: {BG};
}}
QMessageBox QLabel {{
    color: {TEXT}; font: 10pt {FONT};
    background: transparent;
}}
QMessageBox QPushButton, QFileDialog QPushButton {{
    background: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 6px 18px; min-width: 72px;
    font: 500 10pt {FONT};
}}
QMessageBox QPushButton:hover, QFileDialog QPushButton:hover {{
    background: {G50}; border-color: {G200};
}}
QMessageBox QPushButton:pressed, QFileDialog QPushButton:pressed {{
    background: {G100};
}}
QMessageBox QPushButton:default {{
    background: {G400}; color: #FFFFFF; border-color: {G400};
}}
QMessageBox QPushButton:default:hover {{
    background: {G600}; border-color: {G600};
}}
QMenu {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 4px; font: 10pt {FONT};
}}
QMenu::item {{
    padding: 7px 22px 7px 14px; border-radius: 5px; margin: 1px 2px;
}}
QMenu::item:selected {{ background: {G400}; color: #FFFFFF; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 8px; }}
QScrollBar:vertical {{
    background: transparent; width: 10px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: rgba(60,60,67,0.28); border-radius: 5px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: rgba(60,60,67,0.45); }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
QScrollBar:horizontal {{
    background: transparent; height: 10px; margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: rgba(60,60,67,0.28); border-radius: 5px; min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{ background: rgba(60,60,67,0.45); }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
"""


def install(app) -> None:
    """Apply the app-wide typeface and base stylesheet. Call once at startup."""
    app.setStyle("Fusion")
    font = ui_font(10)
    font.setStyleStrategy(QtGui.QFont.PreferAntialias)
    app.setFont(font)
    app.setStyleSheet(APP_STYLESHEET)
