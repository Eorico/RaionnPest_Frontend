from PyQt5.QtGui import QPainter, QPen, QColor as QC, QBrush
from PyQt5.QtCore import QRect, Qt as _Qt
from PyQt5.QtWidgets import QCheckBox

from ui import theme

# macOS-style checkbox: hairline border when empty, solid accent fill when set.
_BOX_RADIUS   = 5
_BORDER_IDLE  = "#C7C7CC"
_BORDER_HOVER = theme.G200
_FILL_HOVER   = theme.G50


class _GreenCheckBox(QCheckBox):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        size  = min(w, h) - 4          # leave a 2 px margin all around
        x     = (w - size) // 2
        y     = (h - size) // 2
        rect  = QRect(x, y, size, size)

        if self.isChecked():
            # ── Filled accent box, no outline (macOS) ────────────────────────
            painter.setPen(_Qt.NoPen)
            painter.setBrush(QBrush(QC(theme.G400)))
            painter.drawRoundedRect(rect, _BOX_RADIUS, _BOX_RADIUS)

            # ── White checkmark ───────────────────────────────────────────────
            pen = QPen(QC("#FFFFFF"), 2.5)
            pen.setCapStyle(_Qt.RoundCap)
            pen.setJoinStyle(_Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(QBrush())           # no fill

            # Checkmark: short left stroke + long right stroke
            cx, cy = x + size // 2, y + size // 2
            painter.drawLine(
                int(x + size * 0.20), int(y + size * 0.52),
                int(x + size * 0.42), int(y + size * 0.72),
            )
            painter.drawLine(
                int(x + size * 0.42), int(y + size * 0.72),
                int(x + size * 0.80), int(y + size * 0.28),
            )

        else:
            # ── Empty box with a hairline border ─────────────────────────────
            hover = self.underMouse()
            border_color = QC(_BORDER_HOVER if hover else _BORDER_IDLE)
            bg_color     = QC(_FILL_HOVER if hover else "#FFFFFF")

            painter.setPen(QPen(border_color, 1.5))
            painter.setBrush(QBrush(bg_color))
            painter.drawRoundedRect(rect, _BOX_RADIUS, _BOX_RADIUS)

        painter.end()

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)