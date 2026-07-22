from PyQt5.QtWidgets import QPushButton, QMessageBox


class ResetToFactoryDefaultsWidget(QPushButton):
    def __init__(self, callback, width=None):
        super().__init__()
        self.setText("Reset to factory defaults")
        self.clicked.connect(lambda: callback() if self.showDialog() == True else None)
        if width != None:
            self.setFixedWidth(width)

    def showDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(
            "Are you sure want to reset all default parameters to factory defaults?\n\nChanges will not be saved, you still need to overwrite settings manually."
        )
        msgBox.setWindowTitle("QUIT")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            return True
        return False
