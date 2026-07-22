from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton

from src.ui.dataViewer import Signal


def get_pollen_types(listWidget):
    return [str(listWidget.item(i).text()) for i in range(listWidget.count())]


class MoveButtonWidget(QPushButton):
    value_changed = pyqtSignal(object)
    UP_MODE = "Up"
    DOWN_MODE = "Down"
    MODES = [UP_MODE, DOWN_MODE]

    def __init__(self, types_signal: Signal, listWidget, mode, width=None):
        super().__init__()
        self.mode = mode
        if self.mode == self.UP_MODE:
            self.setText("↑")
            self.setToolTip("move up")
            self.clicked.connect(lambda: self.on_move_up_button_click(listWidget))
        elif self.mode == self.DOWN_MODE:
            self.setText("↓")
            self.setToolTip("move down")
            self.clicked.connect(lambda: self.on_move_down_button_click(listWidget))
        else:
            raise ValueError(
                f"Unhandled MoveButton mode, mode='{mode}', allowed modes={', '.join(self.MODES)}"
            )
        self.setEnabled(False)
        if width != None:
            self.setFixedWidth(width)
        listWidget.itemSelectionChanged.connect(
            lambda: self.set_state(len(listWidget.selectedItems()) > 0)
        )
        self.value_changed.connect(lambda value: types_signal.value_changed.emit(value))

    def set_state(self, value):
        self.setEnabled(value)

    def change_position(self, listWidget, item, mode, index, step=1):
        currentRow = listWidget.row(item)
        if mode == self.UP_MODE:
            if currentRow == index:
                return
            currentItem = listWidget.takeItem(currentRow)
            listWidget.insertItem(currentRow - step, currentItem)
        elif mode == self.DOWN_MODE:
            items_count = listWidget.count()
            selected_items_count = len(listWidget.selectedItems())
            if items_count == (currentRow + selected_items_count - index):
                return
            currentItem = listWidget.takeItem(currentRow)
            listWidget.insertItem(currentRow + step, currentItem)
        currentItem.setSelected(True)
        value = get_pollen_types(listWidget)
        self.value_changed.emit(value)

    def on_move_up_button_click(self, listWidget):
        [
            self.change_position(listWidget, x, self.mode, idx)
            for idx, x in enumerate(listWidget.selectedItems())
        ]

    def on_move_down_button_click(self, listWidget):
        selected_items = listWidget.selectedItems()
        [
            self.change_position(
                listWidget, x, self.mode, idx, step=len(selected_items)
            )
            for idx, x in enumerate(selected_items)
        ]
