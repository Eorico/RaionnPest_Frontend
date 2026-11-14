# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
import os

base_dir   = os.path.dirname(__file__)
image_path = os.path.join(base_dir, "assets")

# ══════════════════════════════════════════════════════════════════════════════
#  Style constants
# ══════════════════════════════════════════════════════════════════════════════
from ui import theme

_PANEL_LEFT_SS  = f"QWidget#panelLeft {{ background-color: {theme.SIDEBAR_BG}; }}"
_PANEL_RIGHT_SS = f"QWidget#panelRight {{ background-color: {theme.SURFACE}; }}"
_LOGO_LABEL_SS  = "background: transparent; border: none;"

_BRAND_TITLE_SS = f"""
QLabel {{ background: transparent; border: none; color: #FFFFFF;
    font: 600 21pt {theme.FONT_DISPLAY}; letter-spacing: 3px; }}"""

_BRAND_SUB_SS = f"""
QLabel {{ background: transparent; border: none;
    color: rgba(255,255,255,0.52); font: 8pt {theme.FONT};
    letter-spacing: 2.5px; }}"""

_BRAND_RULE_SS = """
QFrame { background-color: rgba(255,255,255,0.16); border: none; max-height: 1px; }"""

_BRAND_TAGLINE_SS = f"""
QLabel {{ background: transparent; border: none;
    color: rgba(255,255,255,0.45); font: 9pt {theme.FONT}; }}"""

_FORM_HEADING_SS = f"""
QLabel {{ background: transparent; border: none;
    color: {theme.TEXT}; font: 600 24pt {theme.FONT_DISPLAY}; }}"""

_FORM_SUB_SS = f"""
QLabel {{ background: transparent; border: none;
    color: {theme.MUTED}; font: 10pt {theme.FONT}; letter-spacing: 0; }}"""

_FIELD_LABEL_SS = f"""
QLabel {{ background: transparent; border: none; color: {theme.MUTED};
    font: 600 8pt {theme.FONT}; letter-spacing: 0.6px; }}"""

_INPUT_SS = f"""
QLineEdit {{
    background-color: {theme.SURFACE}; color: {theme.TEXT};
    border: 1px solid {theme.BORDER}; border-radius: 8px;
    padding: 10px 13px; font: 10pt {theme.FONT};
    selection-background-color: {theme.G100};
    selection-color: {theme.TEXT};
}}
QLineEdit:hover  {{ border-color: #B9BBC1; }}
QLineEdit:focus  {{ border: 1.5px solid {theme.G400}; }}
"""

_LOGIN_BTN_SS = f"""
QPushButton {{
    background-color: {theme.G400}; color: #FFFFFF; border: none;
    border-radius: 8px; font: 600 10pt {theme.FONT};
    letter-spacing: 0; padding: 12px;
}}
QPushButton:hover    {{ background-color: {theme.G600}; }}
QPushButton:pressed  {{ background-color: {theme.G800}; }}
QPushButton:disabled {{ background-color: #C9CBD0; color: #FFFFFF; }}
"""

_FOOTER_SS = f"""
QLabel {{ background: transparent; border: none;
    color: {theme.SUBTLE}; font: 8pt {theme.FONT}; }}"""

_VERSION_SS = f"""
QLabel {{ background: transparent; border: none;
    color: rgba(255,255,255,0.32); font: 8pt {theme.FONT};
    letter-spacing: 0.5px; }}"""


# ══════════════════════════════════════════════════════════════════════════════
#  UI class
# ══════════════════════════════════════════════════════════════════════════════
class Ui_Login(object):

    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.setFixedSize(820, 500)          # ← taller to fit new buttons
        Login.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        Login.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        Login.setStyleSheet("QMainWindow { background: transparent; }")

        self.centralwidget = QtWidgets.QWidget(Login)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet(f"""
            QWidget#centralwidget {{
                background-color: {theme.SURFACE};
                border-radius: 14px;
            }}
        """)
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(48); shadow.setOffset(0, 10)
        shadow.setColor(QtGui.QColor(0, 0, 0, 52))
        self.centralwidget.setGraphicsEffect(shadow)
        Login.setCentralWidget(self.centralwidget)

        h_split = QtWidgets.QHBoxLayout(self.centralwidget)
        h_split.setContentsMargins(0, 0, 0, 0)
        h_split.setSpacing(0)

        # ══════════════════════════════════════════════════════════════════════
        #  LEFT PANEL
        # ══════════════════════════════════════════════════════════════════════
        self.panelLeft = QtWidgets.QWidget()
        self.panelLeft.setObjectName("panelLeft")
        self.panelLeft.setFixedWidth(300)
        self.panelLeft.setStyleSheet(_PANEL_LEFT_SS)

        left_layout = QtWidgets.QVBoxLayout(self.panelLeft)
        left_layout.setContentsMargins(36, 48, 36, 36)
        left_layout.setSpacing(0)
        left_layout.setAlignment(QtCore.Qt.AlignTop)

        self.Logo = QtWidgets.QLabel()
        self.Logo.setFixedSize(90, 90)
        self.Logo.setPixmap(
            QtGui.QPixmap(f"{image_path}/Logo.png").scaled(
                90, 90, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.Logo.setScaledContents(True)
        self.Logo.setStyleSheet(_LOGO_LABEL_SS)
        self.Logo.setAlignment(QtCore.Qt.AlignCenter)
        left_layout.addWidget(self.Logo, 0, QtCore.Qt.AlignHCenter)
        left_layout.addSpacing(22)

        rule_top = QtWidgets.QFrame()
        rule_top.setFrameShape(QtWidgets.QFrame.HLine)
        rule_top.setStyleSheet(_BRAND_RULE_SS)
        left_layout.addWidget(rule_top)
        left_layout.addSpacing(14)

        self.brandTitle = QtWidgets.QLabel("RAIONN")
        self.brandTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.brandTitle.setStyleSheet(_BRAND_TITLE_SS)
        left_layout.addWidget(self.brandTitle)
        left_layout.addSpacing(4)

        self.brandSub = QtWidgets.QLabel("A D M I N   S Y S T E M")
        self.brandSub.setAlignment(QtCore.Qt.AlignCenter)
        self.brandSub.setStyleSheet(_BRAND_SUB_SS)
        left_layout.addWidget(self.brandSub)
        left_layout.addSpacing(14)

        rule_bot = QtWidgets.QFrame()
        rule_bot.setFrameShape(QtWidgets.QFrame.HLine)
        rule_bot.setStyleSheet(_BRAND_RULE_SS)
        left_layout.addWidget(rule_bot)
        left_layout.addSpacing(24)

        self.brandTagline = QtWidgets.QLabel("Secure  ·  Reliable  ·  Efficient")
        self.brandTagline.setAlignment(QtCore.Qt.AlignCenter)
        self.brandTagline.setStyleSheet(_BRAND_TAGLINE_SS)
        self.brandTagline.setWordWrap(True)
        left_layout.addWidget(self.brandTagline)
        left_layout.addStretch()

        self.versionLabel = QtWidgets.QLabel("v 1.0.0")
        self.versionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.versionLabel.setStyleSheet(_VERSION_SS)
        left_layout.addWidget(self.versionLabel)

        h_split.addWidget(self.panelLeft)

        # ══════════════════════════════════════════════════════════════════════
        #  RIGHT PANEL
        # ══════════════════════════════════════════════════════════════════════
        self.panelRight = QtWidgets.QWidget()
        self.panelRight.setObjectName("panelRight")
        self.panelRight.setStyleSheet(_PANEL_RIGHT_SS)

        right_layout = QtWidgets.QVBoxLayout(self.panelRight)
        right_layout.setContentsMargins(52, 0, 52, 0)
        right_layout.setSpacing(0)

        # ── Close button ──────────────────────────────────────────────────────
        top_bar = QtWidgets.QHBoxLayout()
        top_bar.setContentsMargins(0, 16, 0, 0)
        top_bar.addStretch()
        self.closeBtn = QtWidgets.QPushButton(theme.Icon.CLOSE)
        self.closeBtn.setFixedSize(28, 28)
        self.closeBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.closeBtn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none;
                color: {theme.SUBTLE}; font: 9pt {theme.FONT_ICON};
                border-radius: 14px; }}
            QPushButton:hover   {{ background-color: #E8E8ED; color: {theme.TEXT}; }}
            QPushButton:pressed {{ background-color: #DCDCE1; }}
        """)
        self.closeBtn.clicked.connect(Login.close)
        top_bar.addWidget(self.closeBtn)
        top_widget = QtWidgets.QWidget()
        top_widget.setStyleSheet("background: transparent;")
        top_widget.setLayout(top_bar)
        right_layout.addWidget(top_widget)

        right_layout.addSpacing(12)       # ← reduced from addStretch

        # ── Heading ───────────────────────────────────────────────────────────
        self.formHeading = QtWidgets.QLabel("Welcome back")
        self.formHeading.setStyleSheet(_FORM_HEADING_SS)
        right_layout.addWidget(self.formHeading)
        right_layout.addSpacing(3)

        self.formSub = QtWidgets.QLabel("SIGN IN TO CONTINUE")
        self.formSub.setStyleSheet(_FORM_SUB_SS)
        right_layout.addWidget(self.formSub)
        right_layout.addSpacing(20)       # ← reduced from 36

        # ── Username ──────────────────────────────────────────────────────────
        self.usernameLabel = QtWidgets.QLabel("USERNAME")
        self.usernameLabel.setStyleSheet(_FIELD_LABEL_SS)
        right_layout.addWidget(self.usernameLabel)
        right_layout.addSpacing(5)

        self.usernameEdit = QtWidgets.QLineEdit()
        self.usernameEdit.setFixedHeight(44)
        self.usernameEdit.setPlaceholderText("Enter your username")
        self.usernameEdit.setObjectName("usernameEdit")
        self.usernameEdit.setStyleSheet(_INPUT_SS)
        right_layout.addWidget(self.usernameEdit)
        right_layout.addSpacing(14)       # ← reduced from 20

        # ── Password ──────────────────────────────────────────────────────────
        self.passwordLabel = QtWidgets.QLabel("PASSWORD")
        self.passwordLabel.setStyleSheet(_FIELD_LABEL_SS)
        right_layout.addWidget(self.passwordLabel)
        right_layout.addSpacing(5)

        pwd_wrapper = QtWidgets.QWidget()
        pwd_wrapper.setFixedHeight(44)
        pwd_wrapper.setStyleSheet("background: transparent; border: none;")
        pwd_stack = QtWidgets.QStackedLayout(pwd_wrapper)
        pwd_stack.setStackingMode(QtWidgets.QStackedLayout.StackAll)

        self.passwordEdit = QtWidgets.QLineEdit()
        self.passwordEdit.setFixedHeight(44)
        self.passwordEdit.setPlaceholderText("Enter your password")
        self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordEdit.setObjectName("passwordEdit")
        self.passwordEdit.setStyleSheet(_INPUT_SS)
        self.passwordEdit.setTextMargins(0, 0, 44, 0)

        eye_overlay = QtWidgets.QWidget()
        eye_overlay.setStyleSheet("background: transparent; border: none;")
        eye_h = QtWidgets.QHBoxLayout(eye_overlay)
        eye_h.setContentsMargins(0, 0, 6, 0)
        eye_h.addStretch()
        self.eyeBtn = QtWidgets.QPushButton(theme.Icon.EYE_SHOW)
        self.eyeBtn.setFixedSize(34, 34)
        self.eyeBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.eyeBtn.setCheckable(True)
        self.eyeBtn.setToolTip("Show password")
        self.eyeBtn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none;
                color: {theme.SUBTLE}; font: 11pt {theme.FONT_ICON};
                border-radius: 8px; }}
            QPushButton:hover   {{ color: {theme.G400}; background: {theme.BG}; }}
            QPushButton:checked {{ color: {theme.G400}; }}
        """)
        self.eyeBtn.toggled.connect(self._toggle_password)
        eye_h.addWidget(self.eyeBtn, 0, QtCore.Qt.AlignVCenter)
        pwd_stack.addWidget(self.passwordEdit)
        pwd_stack.addWidget(eye_overlay)
        right_layout.addWidget(pwd_wrapper)
        right_layout.addSpacing(16)       # ← reduced from 32

        # ── Divider ───────────────────────────────────────────────────────────
        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setStyleSheet(
            f"background-color: {theme.BORDER}; border: none; max-height: 1px;")
        right_layout.addWidget(divider)
        right_layout.addSpacing(16)       # ← reduced from 28

        # ── Login button ──────────────────────────────────────────────────────
        self.loginbutton = QtWidgets.QPushButton("SIGN IN")
        self.loginbutton.setFixedHeight(46)
        self.loginbutton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.loginbutton.setObjectName("loginbutton")
        self.loginbutton.setStyleSheet(_LOGIN_BTN_SS)
        right_layout.addWidget(self.loginbutton)
        right_layout.addSpacing(8)

        # ── Forgot password link ──────────────────────────────────────────────
        forgot_row = QtWidgets.QHBoxLayout()
        forgot_row.addStretch()
        self.forgotBtn = QtWidgets.QPushButton("Forgot password?")
        self.forgotBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.forgotBtn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none;
                color: {theme.G400}; font: 9pt {theme.FONT}; padding: 4px; }}
            QPushButton:hover   {{ color: {theme.G600}; }}
            QPushButton:pressed {{ color: {theme.G800}; }}
        """)
        forgot_row.addWidget(self.forgotBtn)
        forgot_row.addStretch()
        right_layout.addLayout(forgot_row)
        right_layout.addSpacing(14)

        # ── OR divider ────────────────────────────────────────────────────────
        or_row = QtWidgets.QHBoxLayout()
        or_row.setSpacing(10)
        _line1 = QtWidgets.QFrame()
        _line1.setFrameShape(QtWidgets.QFrame.HLine)
        _line1.setStyleSheet(
            f"background: {theme.BORDER}; max-height: 1px; border: none;")
        _or_lbl = QtWidgets.QLabel("OR")
        _or_lbl.setStyleSheet(
            f"color: {theme.SUBTLE}; font: 8pt {theme.FONT};"
            f" background: transparent; border: none;")
        _line2 = QtWidgets.QFrame()
        _line2.setFrameShape(QtWidgets.QFrame.HLine)
        _line2.setStyleSheet(
            f"background: {theme.BORDER}; max-height: 1px; border: none;")
        or_row.addWidget(_line1, 1)
        or_row.addWidget(_or_lbl)
        or_row.addWidget(_line2, 1)
        right_layout.addLayout(or_row)
        right_layout.addSpacing(14)

        # ── Register button ───────────────────────────────────────────────────
        self.registerBtn = QtWidgets.QPushButton("Create a new account")
        self.registerBtn.setFixedHeight(44)
        self.registerBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.registerBtn.setObjectName("registerBtn")
        self.registerBtn.setStyleSheet(f"""
            QPushButton {{
                background: {theme.SURFACE}; color: {theme.G400};
                border: 1px solid {theme.BORDER}; border-radius: 8px;
                font: 500 10pt {theme.FONT}; letter-spacing: 0;
            }}
            QPushButton:hover   {{ background: {theme.G50};
                                   border-color: {theme.G200}; color: {theme.G600}; }}
            QPushButton:pressed {{ background: {theme.G100}; }}
        """)
        right_layout.addWidget(self.registerBtn)

        right_layout.addStretch(1)

        # ── Footer ────────────────────────────────────────────────────────────
        self.footerLabel = QtWidgets.QLabel(
            "© 2025 Raionn Admin System. All rights reserved.")
        self.footerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.footerLabel.setStyleSheet(_FOOTER_SS)
        right_layout.addWidget(self.footerLabel)
        right_layout.addSpacing(14)

        h_split.addWidget(self.panelRight)

        # ── Window drag ───────────────────────────────────────────────────────
        self._drag_start = None
        Login.mousePressEvent   = self._mouse_press
        Login.mouseMoveEvent    = self._mouse_move
        Login.mouseReleaseEvent = self._mouse_release

        self.retranslateUi(Login)
        QtCore.QMetaObject.connectSlotsByName(Login)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _toggle_password(self, checked):
        if checked:
            self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.eyeBtn.setText(theme.Icon.EYE_HIDE)
            self.eyeBtn.setToolTip("Hide password")
        else:
            self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
            self.eyeBtn.setText(theme.Icon.EYE_SHOW)
            self.eyeBtn.setToolTip("Show password")

    def _mouse_press(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start = event.globalPos()

    def _mouse_move(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self._drag_start is not None:
            delta = event.globalPos() - self._drag_start
            win = self.centralwidget.parent()
            win.move(win.pos() + delta)
            self._drag_start = event.globalPos()

    def _mouse_release(self, event):
        self._drag_start = None

    def retranslateUi(self, Login):
        Login.setWindowTitle(
            QtCore.QCoreApplication.translate("Login", "Raionn Admin — Login"))


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    Login = QtWidgets.QMainWindow()
    ui = Ui_Login()
    ui.setupUi(Login)
    Login.show()
    sys.exit(app.exec_())