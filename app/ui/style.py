# -*- coding: utf-8 -*-
"""Shared control styles. Colours and type come from ui/theme.py."""
from ui import theme

# ── Row "Edit" button — macOS bordered push button ───────────────────────────
btn_style = f"""
QPushButton {{
    background: {theme.SURFACE};
    color: {theme.G400};
    border: 1px solid {theme.BORDER};
    border-radius: 6px;
    padding: 5px 14px;
    font: 500 9pt {theme.FONT};
}}
QPushButton:hover {{
    background: {theme.G50};
    border-color: {theme.G200};
    color: {theme.G600};
}}
QPushButton:pressed {{
    background: {theme.G100};
    border-color: {theme.G400};
}}
"""

# Same button on a selected (tinted) row — keeps the control legible.
BTN_EDIT_ON_SELECTION = f"""
QPushButton {{
    background: {theme.SURFACE};
    color: {theme.G600};
    border: 1px solid {theme.G200};
    border-radius: 6px;
    padding: 5px 14px;
    font: 500 9pt {theme.FONT};
}}
QPushButton:hover {{ background: {theme.G50}; border-color: {theme.G400}; }}
"""

_BTN_EDIT_LOCKED = f"""
QPushButton {{
    background: {theme.BG};
    color: {theme.SUBTLE};
    border: 1px solid {theme.GRID};
    border-radius: 6px;
    padding: 5px 14px;
    font: 9pt {theme.FONT};
}}
"""

# ── Generic dialog (used by the smaller popups) ──────────────────────────────
edit_style = f"""
QDialog {{ background: {theme.BG}; }}
QLabel  {{
    font: 10pt {theme.FONT}; color: {theme.TEXT}; background: transparent;
}}
QLineEdit, QComboBox {{
    background: {theme.SURFACE};
    border: 1px solid {theme.BORDER};
    border-radius: 7px;
    padding: 7px 10px;
    font: 10pt {theme.FONT};
    color: {theme.TEXT};
    min-height: 20px;
}}
QLineEdit:focus, QComboBox:focus {{
    border: 1.5px solid {theme.G400};
}}
QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{
    background: {theme.SURFACE};
    border: 1px solid {theme.BORDER};
    border-radius: 7px;
    selection-background-color: {theme.G400};
    selection-color: #FFFFFF;
    font: 10pt {theme.FONT};
}}
QTableWidget {{
    background: {theme.SURFACE};
    font: 10pt {theme.FONT};
    color: {theme.TEXT};
    border: 1px solid {theme.BORDER};
    border-radius: 8px;
    gridline-color: {theme.GRID};
}}
QHeaderView::section {{
    background: {theme.G400};
    color: #FFFFFF;
    font: 600 9pt {theme.FONT};
    border: none;
    padding: 7px 10px;
}}
QPushButton {{
    background: {theme.G400};
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 8px 18px;
    font: 600 10pt {theme.FONT};
}}
QPushButton:hover   {{ background: {theme.G600}; }}
QPushButton:pressed {{ background: {theme.G800}; }}
"""
