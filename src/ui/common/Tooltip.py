from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFrame,
    QLabel,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QObject, QEvent
from PyQt5.QtGui import QFont, QColor


class TooltipWrapper(QFrame):
    """
    A lightweight, web-style tooltip widget.

    Methods:
        start(pos: QPoint): Schedule tooltip to show at global pos after delay
        stop(): Cancel pending show and hide
    """

    def __init__(self, text: str, parent=None, delay: int = 500):
        super().__init__(parent, flags=Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._delay = delay
        self._target_pos = QPoint()

        # Styling
        self.setStyleSheet(
            "QFrame {"
            " background-color: #333;"
            " color: #fff;"
            " border-radius: 5px;"
            " padding: 8px;"
            "}"
        )

        # Rich-text label
        self.label = QLabel(text, self)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("SansSerif", 10))
        self.label.setTextFormat(Qt.RichText)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        if text != None and len(text) > 60:
            self.label.setFixedWidth(300)
        if text != None and len(text) > 300:
            self.label.setFixedWidth(500)
        layout.addWidget(self.label)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        # Show timer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show)

    def start(self, global_pos: QPoint):
        """Schedule tooltip to appear at the given global position (on hover)."""
        self._target_pos = global_pos
        self._timer.start(self._delay)

    def stop(self):
        """Hide the tooltip and cancel pending show (on hover leave)."""
        self._timer.stop()
        self.hide()

    def _show(self):
        """Internal slot to display the tooltip."""
        self.move(self._target_pos)
        self.adjustSize()
        self.show()


class Tooltip(QObject):
    """
    Event filter for hover behavior:
      - on Enter (hover): show tooltip after delay
      - on Leave: hide immediately

    Usage:
        widget.installEventFilter(ToolTipFilter("Your tooltip text", parent=widget))
    """

    def __init__(self, text: str, parent=None, delay=0):
        super().__init__(parent)
        self._tooltip = TooltipWrapper(text, parent=parent, delay=delay)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            # Show tooltip just below widget on hover
            pos = obj.mapToGlobal(obj.rect().bottomLeft()) + QPoint(0, 5)
            self._tooltip.start(pos)
        elif event.type() == QEvent.Leave:
            # Hide tooltip when hover ends
            self._tooltip.stop()
        return super().eventFilter(obj, event)
