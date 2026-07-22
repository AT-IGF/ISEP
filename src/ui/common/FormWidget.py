from functools import partial
from src.ui.common.General import set_style_sheet
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QListWidget,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)


class SubApp:
    def __init__(self, app_name, widget):
        self.app_name = app_name
        self.button = QPushButton(app_name)
        self.widget = widget


class FormWidget(QWidget):
    def __init__(self, parent, sub_apps):
        super(FormWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        layoutApps = QHBoxLayout(self)

        self.sub_apps = sub_apps

        for sub_app in self.sub_apps:
            layoutApps.addWidget(sub_app.button)
            sub_app.button.clicked.connect(
                partial(self.on_app_button_click, self.sub_apps, sub_app)
            )  # https://stackoverflow.com/questions/67057972/pyqt5-clicked-button-created-in-loop
            self.layout.addWidget(sub_app.widget)

        self.layout.insertLayout(0, layoutApps)
        self.setLayout(self.layout)
        self.on_app_button_click(self.sub_apps, self.sub_apps[0])

    def on_app_button_click(self, sub_apps: list[SubApp], sub_app):
        for _sub_app in sub_apps:
            if _sub_app is sub_app:
                _sub_app.widget.show()
                _sub_app.button.setStyleSheet("font-weight: bold")
            else:
                _sub_app.widget.hide()
                _sub_app.button.setStyleSheet("font-weight: normal")
