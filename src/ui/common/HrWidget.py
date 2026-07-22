from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame


class HrWidget(QWidget):
    def __init__(self):
        super().__init__()

        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)  # horizontal line
        hline.setFrameShadow(QFrame.Sunken)  # give it a sunken/shadowed look
        # (alternatively: Plain, Raised, or no shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        layout.addWidget(hline)
        self.setLayout(layout)
