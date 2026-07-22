import logging

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QPlainTextEdit,
    QDialog,
    QApplication,
)
from matplotlib import pyplot as plt


class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit(parent)
        self.app = QApplication.instance()
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendPlainText)
        self.widget.setMaximumBlockCount(2000)
        self.widget.setFont(
            QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        )
        self.widget.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

    def emit(self, record):
        if isinstance(record, logging.LogRecord):
            msg = self.format(record)
        elif isinstance(record, tuple) and len(record) == 2:
            tag, text = record
            msg = f"{tag}: {text}"
        else:
            msg = str(record)
        self.appendPlainText.emit(msg)

    def clear(self):
        self.widget.clear()


class LoggerDialog(QDialog):
    cancel_task = pyqtSignal()

    def __init__(self, title: str, name=None):
        super().__init__()
        QObject.__init__(self)
        self.app = QApplication.instance()
        self._logger_name = name
        self.show_cancel_modal = True
        self.setWindowTitle(title)
        self.logTextBox = QTextEditLogger(self)
        self.setMinimumSize(800, 400)
        layout = QVBoxLayout()
        layout.addWidget(self.logTextBox.widget)
        self.logTextBox.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        self.add_logger_to_TextBox(name)
        self.add_logger_to_TextBox(None)

        self.setLayout(layout)

    def show(self):
        self.logTextBox.clear()
        super().show()

    def logger_exists(self, name: str) -> bool:
        return name in logging.Logger.manager.loggerDict

    def add_logger_to_TextBox(self, logger_name):
        if logger_name != None and self.logger_exists(logger_name):
            return
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.addFilter(self.on_log)

    def closeEvent(self, event):
        if not self.show_cancel_modal:
            event.accept()
            return

        click_event = self.showDialog()
        if click_event == QMessageBox.Cancel:
            event.ignore()
            return

        if click_event == QMessageBox.Abort:
            event.ignore()
        else:
            event.accept()

        self.cancel_task.emit()
        plt.close("all")

    def showDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("The process is still running")
        msgBox.setWindowTitle("Stop process?")
        msgBox.setStandardButtons(
            QMessageBox.Abort | QMessageBox.Close | QMessageBox.Cancel
        )

        return msgBox.exec()

    def on_log(self, record):
        if self.isVisible():
            self.logTextBox.emit(record)
            self.app.processEvents()
        return True

    def appendPlainText(self, record):
        self.logTextBox.widget.appendPlainText(record)
