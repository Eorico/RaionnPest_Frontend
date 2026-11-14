# login/forgot_password_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QStackedWidget,
    QGraphicsDropShadowEffect, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QCursor, QFont
import re

from ui import theme

_G400   = theme.G400
_G600   = theme.G600
_G100   = theme.G100
_BG     = theme.SURFACE
_BORDER = theme.BORDER
_MUTED  = theme.MUTED

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
QLineEdit:hover {{ border-color: #B9BBC1; }}
QLineEdit:focus {{ border: 1.5px solid {theme.G400}; }}
"""

# One-time code: wide tracking, tabular figures, neutral field.
_OTP_SS = f"""
QLineEdit {{
    background: {theme.SURFACE};
    color: {theme.TEXT};
    border: 1px solid {theme.BORDER};
    border-radius: 10px;
    font: 600 20pt {theme.FONT_DISPLAY};
    letter-spacing: 10px;
    padding: 12px;
    qproperty-alignment: AlignCenter;
}}
QLineEdit:focus {{ border: 1.5px solid {theme.G400}; background: {theme.SURFACE}; }}
"""

_BTN_PRIMARY_SS = f"""
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

_BTN_LINK_SS = f"""
QPushButton {{
    background: transparent; border: none;
    color: {theme.G400}; font: 9pt {theme.FONT};
    padding: 4px 2px;
}}
QPushButton:hover    {{ color: {theme.G600}; }}
QPushButton:pressed  {{ color: {theme.G800}; }}
QPushButton:disabled {{ color: {theme.SUBTLE}; }}
"""

_LBL_CAP_SS = f"""
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
_OK_SS = f"""QLabel {{
    color: {theme.G600}; font: 9pt {theme.FONT};
    background: {theme.G50}; border: 1px solid {theme.G100};
    border-radius: 7px; padding: 8px 11px;
}}"""
_HIDDEN_SS = "QLabel { background: transparent; border: none; }"


def _extract_email(text) -> str:
    """Pick the address out of a message like "Code sent to a***@gmail.com"."""
    match = re.search(r"\S+@\S+", str(text or ""))
    return match.group(0).rstrip(".,;") if match else ""


class ForgotPasswordDialog(QDialog):
    def __init__(self, api_service, parent=None):
        super().__init__(parent)
        self.api             = api_service
        self._username       = ""
        self._drag           = None
        self._resend_seconds = 0
        self._resend_timer   = QTimer(self)
        self._resend_timer.timeout.connect(self._tick_resend)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(460)
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)

        self._card = QFrame()
        self._card.setObjectName("authCard")
        # Scoped by object name: an unscoped "QFrame" rule also paints every
        # child frame (the stacked pages, the dividers) with this border.
        self._card.setStyleSheet(f"""
            QFrame#authCard {{
                background: {theme.SURFACE};
                border-radius: 14px;
                border: 1px solid {theme.BORDER};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(44)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 46))
        self._card.setGraphicsEffect(shadow)
        outer.addWidget(self._card)

        root = QVBoxLayout(self._card)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Colored top band ──────────────────────────────────────────────────
        band = QFrame()
        band.setFixedHeight(3)
        band.setStyleSheet(
            f"background: {theme.G400}; border: none; border-radius: 3px 3px 0 0;")
        root.addWidget(band)

        # ── Content area ──────────────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(40, 28, 40, 32)
        content_lay.setSpacing(0)

        # Close button row
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton(theme.Icon.CLOSE)
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none;
                color: {theme.SUBTLE}; font: 9pt {theme.FONT_ICON};
                border-radius: 14px; }}
            QPushButton:hover   {{ background: #E8E8ED; color: {theme.TEXT}; }}
            QPushButton:pressed {{ background: #DCDCE1; }}
        """)
        close_btn.clicked.connect(self.reject)
        close_row.addWidget(close_btn)
        content_lay.addLayout(close_row)
        content_lay.addSpacing(4)

        # Icon
        icon_lbl = QLabel(theme.Icon.LOCK)
        icon_lbl.setFixedSize(52, 52)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            f"font: 20pt {theme.FONT_ICON}; color: {theme.G400};"
            f" background: {theme.G50}; border: 1px solid {theme.G100};"
            f" border-radius: 26px;")
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_lbl)
        icon_row.addStretch()
        content_lay.addLayout(icon_row)
        content_lay.addSpacing(10)

        # Title + subtitle (updatable)
        self._title = QLabel("Forgot Password")
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet(
            f"color: {theme.TEXT}; font: 600 17pt {theme.FONT_DISPLAY};"
            f" background: transparent; border: none;")
        content_lay.addWidget(self._title)
        content_lay.addSpacing(6)

        self._subtitle = QLabel("Enter your username to receive a reset code.")
        self._subtitle.setAlignment(Qt.AlignCenter)
        self._subtitle.setWordWrap(True)
        self._subtitle.setStyleSheet(
            f"color: {theme.MUTED}; font: 10pt {theme.FONT};"
            f" background: transparent; border: none;")
        content_lay.addWidget(self._subtitle)
        content_lay.addSpacing(24)

        # Stacked pages
        self._stack = QStackedWidget()
        self._stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._stack.addWidget(self._build_step1())
        self._stack.addWidget(self._build_step2())
        content_lay.addWidget(self._stack)

        root.addWidget(content)

        # Drag
        self._card.mousePressEvent   = self._drag_press
        self._card.mouseMoveEvent    = self._drag_move
        self._card.mouseReleaseEvent = self._drag_release

    def _build_step1(self) -> QWidget:
        w   = QWidget(); w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lbl = QLabel("USERNAME")
        lbl.setStyleSheet(_LBL_CAP_SS)
        lay.addWidget(lbl)
        lay.addSpacing(6)

        self.usernameEdit = QLineEdit()
        self.usernameEdit.setFixedHeight(44)
        self.usernameEdit.setPlaceholderText("Enter your username")
        self.usernameEdit.setStyleSheet(_INPUT_SS)
        self.usernameEdit.returnPressed.connect(self._send_code)
        lay.addWidget(self.usernameEdit)
        lay.addSpacing(14)

        # Status (hidden by default)
        self._step1Status = QLabel("")
        self._step1Status.setWordWrap(True)
        self._step1Status.setStyleSheet(_HIDDEN_SS)
        self._step1Status.setFixedHeight(0)
        lay.addWidget(self._step1Status)
        lay.addSpacing(6)

        self._sendBtn = QPushButton("SEND RESET CODE")
        self._sendBtn.setFixedHeight(46)
        self._sendBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self._sendBtn.setStyleSheet(_BTN_PRIMARY_SS)
        self._sendBtn.clicked.connect(self._send_code)
        lay.addWidget(self._sendBtn)
        lay.addSpacing(16)

        # Back link
        back_row = QHBoxLayout()
        back_row.addStretch()
        back_btn = QPushButton("Back to sign in")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet(_BTN_LINK_SS)
        back_btn.clicked.connect(self.reject)
        back_row.addWidget(back_btn)
        back_row.addStretch()
        lay.addLayout(back_row)
        return w

    def _build_step2(self) -> QWidget:
        w   = QWidget(); w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Sent confirmation chip
        self._codeSentLbl = QLabel("")
        self._codeSentLbl.setWordWrap(True)
        self._codeSentLbl.setAlignment(Qt.AlignCenter)
        self._codeSentLbl.setStyleSheet(_HIDDEN_SS)
        lay.addWidget(self._codeSentLbl)
        lay.addSpacing(14)

        # OTP box
        otp_lbl = QLabel("VERIFICATION CODE")
        otp_lbl.setStyleSheet(_LBL_CAP_SS)
        lay.addWidget(otp_lbl)
        lay.addSpacing(6)

        self.otpEdit = QLineEdit()
        self.otpEdit.setFixedHeight(60)
        self.otpEdit.setMaxLength(6)
        self.otpEdit.setAlignment(Qt.AlignCenter)
        self.otpEdit.setPlaceholderText("000000")
        self.otpEdit.setStyleSheet(_OTP_SS)
        lay.addWidget(self.otpEdit)
        lay.addSpacing(18)

        # Divider
        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(
            f"background: {theme.BORDER}; max-height: 1px; border: none;")
        lay.addWidget(div)
        lay.addSpacing(18)

        # New password
        pw_lbl = QLabel("NEW PASSWORD")
        pw_lbl.setStyleSheet(_LBL_CAP_SS)
        lay.addWidget(pw_lbl)
        lay.addSpacing(6)
        self.newPwEdit = QLineEdit()
        self.newPwEdit.setFixedHeight(44)
        self.newPwEdit.setEchoMode(QLineEdit.Password)
        self.newPwEdit.setPlaceholderText("At least 8 characters")
        self.newPwEdit.setStyleSheet(_INPUT_SS)
        lay.addWidget(self.newPwEdit)
        lay.addSpacing(10)

        confirm_lbl = QLabel("CONFIRM PASSWORD")
        confirm_lbl.setStyleSheet(_LBL_CAP_SS)
        lay.addWidget(confirm_lbl)
        lay.addSpacing(6)
        self.confirmPwEdit = QLineEdit()
        self.confirmPwEdit.setFixedHeight(44)
        self.confirmPwEdit.setEchoMode(QLineEdit.Password)
        self.confirmPwEdit.setPlaceholderText("Repeat new password")
        self.confirmPwEdit.setStyleSheet(_INPUT_SS)
        lay.addWidget(self.confirmPwEdit)
        lay.addSpacing(14)

        # Status
        self._step2Status = QLabel("")
        self._step2Status.setWordWrap(True)
        self._step2Status.setStyleSheet(_HIDDEN_SS)
        lay.addWidget(self._step2Status)
        lay.addSpacing(6)

        self._resetBtn = QPushButton("RESET PASSWORD")
        self._resetBtn.setFixedHeight(46)
        self._resetBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self._resetBtn.setStyleSheet(_BTN_PRIMARY_SS)
        self._resetBtn.clicked.connect(self._reset_password)
        lay.addWidget(self._resetBtn)
        lay.addSpacing(16)

        # Resend + back row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        bottom_row.addStretch()
        self._resendBtn = QPushButton("Resend code")
        self._resendBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self._resendBtn.setStyleSheet(_BTN_LINK_SS)
        self._resendBtn.clicked.connect(self._resend_code)
        bottom_row.addWidget(self._resendBtn)

        sep = QLabel("·")
        sep.setStyleSheet(
            f"color: {theme.SUBTLE}; background: transparent; border: none;")
        bottom_row.addWidget(sep)

        back_btn = QPushButton("Back")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet(_BTN_LINK_SS)
        back_btn.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        bottom_row.addWidget(back_btn)
        bottom_row.addStretch()
        lay.addLayout(bottom_row)
        return w

    # ── Drag ─────────────────────────────────────────────────────────────────
    def _drag_press(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPos()

    def _drag_move(self, e):
        if e.buttons() == Qt.LeftButton and self._drag is not None:
            self.move(self.pos() + e.globalPos() - self._drag)
            self._drag = e.globalPos()

    def _drag_release(self, e):
        self._drag = None

    # ── Step 1 ────────────────────────────────────────────────────────────────
    def _send_code(self):
        username = self.usernameEdit.text().strip()
        if not username:
            self._show_status(self._step1Status, "Please enter your username.", error=True)
            return

        self._sendBtn.setEnabled(False)
        self._sendBtn.setText("Sending…")
        self._step1Status.setStyleSheet(_HIDDEN_SS)
        self._step1Status.setFixedHeight(0)

        success, msg = self.api.forgot_password_service(username)

        self._sendBtn.setEnabled(True)
        self._sendBtn.setText("SEND RESET CODE")

        if success:
            self._username = username
            email = _extract_email(msg)
            self._title.setText("Check your email")
            self._subtitle.setText(
                f"We sent a 6-digit code to {email}."
                if email else "We sent you a 6-digit verification code."
            )
            self._show_status(self._codeSentLbl, f"✓  {msg}", error=False)
            self.otpEdit.clear()
            self.newPwEdit.clear()
            self.confirmPwEdit.clear()
            self._step2Status.setStyleSheet(_HIDDEN_SS)
            self._stack.setCurrentIndex(1)
            self.adjustSize()
            self._start_resend_cooldown(60)
        else:
            self._show_status(self._step1Status, msg, error=True)

    # ── Step 2 ────────────────────────────────────────────────────────────────
    def _reset_password(self):
        otp        = self.otpEdit.text().strip()
        new_pw     = self.newPwEdit.text()
        confirm_pw = self.confirmPwEdit.text()

        if len(otp) != 6 or not otp.isdigit():
            self._show_status(self._step2Status,
                              "Enter the 6-digit code from your email.", error=True)
            return
        if len(new_pw) < 8:
            self._show_status(self._step2Status,
                              "Password must be at least 8 characters.", error=True)
            return
        if new_pw != confirm_pw:
            self._show_status(self._step2Status,
                              "Passwords do not match.", error=True)
            return

        self._resetBtn.setEnabled(False)
        self._resetBtn.setText("Resetting…")

        success, msg = self.api.reset_password_service(self._username, otp, new_pw)

        self._resetBtn.setEnabled(True)
        self._resetBtn.setText("RESET PASSWORD")

        if success:
            self._show_status(self._step2Status,
                              "Password reset. You can now sign in.", error=False)
            self._resetBtn.setEnabled(False)
            self._resendBtn.setEnabled(False)
            self._resend_timer.stop()
        else:
            self._show_status(self._step2Status, msg, error=True)

    def _resend_code(self):
        success, msg = self.api.forgot_password_service(self._username)
        if success:
            self._show_status(self._codeSentLbl, f"✓  New code sent. {msg}", error=False)
            self._start_resend_cooldown(60)
        else:
            self._show_status(self._step2Status, msg, error=True)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _show_status(self, lbl: QLabel, text, error: bool):
        lbl.setStyleSheet(_ERR_SS if error else _OK_SS)
        lbl.setText(str(text) if text else "")
        lbl.setFixedHeight(lbl.sizeHint().height() + 8)

    def _start_resend_cooldown(self, seconds: int):
        self._resend_seconds = seconds
        self._resendBtn.setEnabled(False)
        self._tick_resend()
        self._resend_timer.start(1000)

    def _tick_resend(self):
        if self._resend_seconds <= 0:
            self._resend_timer.stop()
            self._resendBtn.setEnabled(True)
            self._resendBtn.setText("Resend code")
        else:
            self._resendBtn.setText(f"Resend ({self._resend_seconds}s)")
            self._resend_seconds -= 1