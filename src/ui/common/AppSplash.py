from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt


class AppSplash(QSplashScreen):
    def __init__(self, title="ISEP", width=400, height=200):
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#2b2b2b"))

        painter = QPainter(pixmap)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 24))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, f"{title}")

        painter.setPen(QColor("#888888"))
        painter.setFont(QFont("Arial", 12))
        rect = pixmap.rect()
        rect.setTop(rect.center().y() + 20)
        painter.drawText(rect, Qt.AlignHCenter | Qt.AlignTop, "\nLoading...")

        painter.end()

        super().__init__(pixmap)
