# login/register_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor

from ui import theme

_G400   = theme.G400
_G600   = theme.G600
_G100   = theme.G100
_BG     = theme.SURFACE
_BORDER = theme.BORDER
_MUTED  = theme.MUTED

# Text fields: white, hairline border, accent ring on focus.
_INPUT_SS = f"""
QLineEdit {{
    background: {theme.SURFACE};
    color: {theme.TEXT};
    border: 1px solid {theme.BORDER};
    border-radius: 8px;
    padding: 10px 13px;
    font: 10pt {theme.FONT};
    selection-background-color: {theme.G100};
    selection-color: {theme.TEXT};
}}
QLineEdit:hover  {{ border-color: #B9BBC1; }}
QLineEdit:focus  {{ border: 1.5px solid {theme.G400}; background: {theme.SURFACE}; }}
"""

# Filled primary button — no letter-spacing: macOS buttons are not tracked.
_BTN_SS = f"""
QPushButton {{
    background: {theme.G400};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font: 600 10pt {theme.FONT};
    padding: 12px;
}}
QPushButton:hover    {{ background: {theme.G600}; }}
QPushButton:pressed  {{ background: {theme.G800}; }}
QPushButton:disabled {{ background: #C9CBD0; color: #FFFFFF; }}
"""

# Plain accent link — macOS links are not underlined inside app chrome.
_LINK_SS = f"""
QPushButton {{
    background: transparent; border: none;
    color: {theme.G400}; font: 9pt {theme.FONT};
    padding: 4px 2px;
}}
QPushButton:hover   {{ color: {theme.G600}; }}
QPushButton:pressed {{ color: {theme.G800}; }}
"""

# Field caption: small, semibold, secondary — light tracking, not 2px.
_LBL_SS = f"""
QLabel {{
    background: transparent; border: none;
    color: {theme.MUTED}; font: 600 8pt {theme.FONT};
    letter-spacing: 0.6px;
}}
"""

_ERR_SS = f"""QLabel {{
    color: {theme.RED}; font: 9pt {theme.FONT};
    background: {theme.RED_BG}; border: 1px solid #F6C9C5;
    border-radius: 7px; padding: 8px 11px;
}}"""
_HIDDEN_SS = "QLabel { background: transparent; border: none; }"
_OK_SS = f"""QLabel {{
    color: {theme.G600}; font: 9pt {theme.FONT};
    background: {theme.G50}; border: 1px solid {theme.G100};
    border-radius: 7px; padding: 8px 11px;
}}"""


class RegisterDialog(QDialog):
    def __init__(self, api_service, parent=None):
        super().__init__(parent)
        self.api   = api_service
        self._drag = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(420)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        self._card = QFrame()
        self._card.setObjectName("authCard")
        # Scoped by object name — an unscoped "QFrame" rule would also paint
        # every child frame with this border.
        self._card.setStyleSheet(f"""
            QFrame#authCard {{ background: {theme.SURFACE}; border-radius: 14px;
                     border: 1px solid {theme.BORDER}; }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(44); shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 46))
        self._card.setGraphicsEffect(shadow)
        outer.addWidget(self._card)

        lay = QVBoxLayout(self._card)
        lay.setContentsMargins(40, 36, 40, 36)
        lay.setSpacing(0)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Create Account")
        title.setStyleSheet(
            f"color: {theme.TEXT}; font: 600 17pt {theme.FONT_DISPLAY};"
            f" background: transparent; border: none;")
        hdr.addWidget(title)
        hdr.addStretch()
        close_btn = QPushButton(theme.Icon.CLOSE)
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none;
                color: {theme.SUBTLE}; font: 9pt {theme.FONT_ICON};
                border-radius: 13px; }}
            QPushButton:hover   {{ background: #E8E8ED; color: {theme.TEXT}; }}
            QPushButton:pressed {{ background: #DCDCE1; }}
        """)
        close_btn.clicked.connect(self.reject)
        hdr.addWidget(close_btn)
        lay.addLayout(hdr)
        lay.addSpacing(4)

        sub = QLabel("Fill in the details to register a new admin")
        sub.setStyleSheet(
            f"color: {theme.MUTED}; font: 9pt {theme.FONT};"
            f" background: transparent; border: none;")
        lay.addWidget(sub)
        lay.addSpacing(24)

        def _field(label_txt, placeholder, echo=False):
            lbl = QLabel(label_txt)
            lbl.setStyleSheet(_LBL_SS)
            lay.addWidget(lbl)
            lay.addSpacing(5)
            edit = QLineEdit()
            edit.setFixedHeight(44)
            edit.setPlaceholderText(placeholder)
            edit.setStyleSheet(_INPUT_SS)
            if echo:
                edit.setEchoMode(QLineEdit.Password)
            lay.addWidget(edit)
            lay.addSpacing(14)
            return edit

        self.usernameEdit = _field("USERNAME", "Choose a username")
        self.emailEdit    = _field("EMAIL", "your@gmail.com")
        self.passwordEdit = _field("PASSWORD", "At least 8 characters", echo=True)
        self.confirmEdit  = _field("CONFIRM PASSWORD", "Repeat password", echo=True)

        # ── Enter-key navigation between fields ───────────────────────────────
        self.usernameEdit.returnPressed.connect(self.emailEdit.setFocus)
        self.emailEdit.returnPressed.connect(self.passwordEdit.setFocus)
        self.passwordEdit.returnPressed.connect(self.confirmEdit.setFocus)
        self.confirmEdit.returnPressed.connect(self._attempt_register)

        self.statusLbl = QLabel("")
        self.statusLbl.setWordWrap(True)
        self.statusLbl.setStyleSheet(_HIDDEN_SS)   # no empty chip on open
        lay.addWidget(self.statusLbl)
        lay.addSpacing(6)

        self.registerBtn = QPushButton("CREATE ACCOUNT")
        self.registerBtn.setFixedHeight(46)
        self.registerBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.registerBtn.setStyleSheet(_BTN_SS)
        self.registerBtn.clicked.connect(self._attempt_register)
        lay.addWidget(self.registerBtn)
        lay.addSpacing(16)

        back_row = QHBoxLayout()
        back_row.addStretch()
        back_btn = QPushButton("Already have an account? Sign in")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet(_LINK_SS)
        back_btn.clicked.connect(self.reject)
        back_row.addWidget(back_btn)
        back_row.addStretch()
        lay.addLayout(back_row)

        # ── Drag — use proper methods, NOT value-returning lambdas ────────────
        self._card.mousePressEvent   = self._drag_press
        self._card.mouseMoveEvent    = self._drag_move
        self._card.mouseReleaseEvent = self._drag_release

    # ── Drag handlers (return None — required by PyQt5) ───────────────────────
    def _drag_press(self, event):
        if event.button() == Qt.LeftButton:
            self._drag = event.globalPos()

    def _drag_move(self, event):
        if event.buttons() == Qt.LeftButton and self._drag is not None:
            self.move(self.pos() + event.globalPos() - self._drag)
            self._drag = event.globalPos()

    def _drag_release(self, event):
        self._drag = None

    # ── Register logic ────────────────────────────────────────────────────────
    def _attempt_register(self):
        username = self.usernameEdit.text().strip()
        email    = self.emailEdit.text().strip()
        password = self.passwordEdit.text()
        confirm  = self.confirmEdit.text()

        if not all([username, email, password, confirm]):
            self._err("All fields are required.")
            return
        if len(password) < 8:
            self._err("Password must be at least 8 characters.")
            return
        if password != confirm:
            self._err("Passwords do not match.")
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            self._err("Enter a valid email address.")
            return

        self.registerBtn.setEnabled(False)
        self.registerBtn.setText("Creating…")

        success, msg = self.api.register_service(username, password, email)

        self.registerBtn.setEnabled(True)
        self.registerBtn.setText("CREATE ACCOUNT")

        if success:
            self.statusLbl.setStyleSheet(_OK_SS)   # chip appears with the text
            self.statusLbl.setText("Account created. You can now sign in.")
            self.registerBtn.setEnabled(False)
        else:
            self._err(msg)

    def _err(self, text):
        self.statusLbl.setStyleSheet(_ERR_SS)
        self.statusLbl.setText(str(text) if text else "")