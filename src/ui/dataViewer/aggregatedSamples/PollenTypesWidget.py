# from PyQt5.QtCore import Qt, pyqtSignal
# from PyQt5.QtWidgets import QWidget, QMessageBox, QListWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QAbstractItemView

# from src.ui.common import IconLabel
# from src.common.config import Config
# from src.common.config.configs import ModelRunnerConfig

# class ListWidget(QListWidget):
#    def Clicked(self,item):
#       QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())


# class PollenTypesWidget(QWidget):
#     value_changed = pyqtSignal(object)
#     show_modal = pyqtSignal(object)

#     def __init__(self):
#         super().__init__()
#         label = QLabel("Pollen types")
#         pollen_types_help = IconLabel("mdi.help-circle-outline", tooltip="Particle type names that model will be predicting. Count and order must be equivalent to the selected model.", color="darkBlue")
#         listWidget = self.pollen_types_list_widget()
#         self.pollen_types = self.get_pollen_types(listWidget)
#         self.pollen_types_original = self.get_pollen_types(listWidget)
#         layoutV = QVBoxLayout()
#         layoutH = QHBoxLayout()
#         layoutH.addWidget(label)
#         layoutH.addWidget(pollen_types_help)
#         layoutV.addLayout(layoutH)
#         layoutV.addWidget(listWidget)

#         def update_icon_state(is_combined_enabled: bool):
#             if is_combined_enabled:
#                 self.file_exists_warning_icon.hide()
#             else:
#                 self.update_tooltip(listWidget)

#         self.update_icon_state = update_icon_state

#         layoutVOptions = QVBoxLayout()

#         remove_button = QPushButton("Remove")
#         remove_button.setEnabled(False)
#         remove_button.clicked.connect(lambda: self.on_remove_button_click(listWidget))
#         reset_button = QPushButton("⟳")
#         reset_button.clicked.connect(lambda: self.on_reset_button_click(listWidget))
#         move_up_button = QPushButton("↑")
#         move_up_button.setEnabled(False)
#         move_up_button.clicked.connect(lambda: self.on_move_up_button_click(listWidget))
#         move_down_button = QPushButton("↓")
#         move_down_button.setEnabled(False)
#         move_down_button.clicked.connect(lambda: self.on_move_down_button_click(listWidget))
#         layoutVOptions
#         layoutVOptions.addWidget(reset_button)
#         layoutVOptions.addWidget(remove_button)
#         layoutVOptions.addWidget(move_up_button)
#         layoutVOptions.addWidget(move_down_button)
#         layoutVOptions.setAlignment(Qt.AlignCenter)

#         listWidget.itemSelectionChanged.connect(lambda: remove_button.setEnabled(len(listWidget.selectedItems()) > 0))
#         listWidget.itemSelectionChanged.connect(lambda: move_up_button.setEnabled(len(listWidget.selectedItems()) > 0))
#         listWidget.itemSelectionChanged.connect(lambda: move_down_button.setEnabled(len(listWidget.selectedItems()) > 0))

#         layoutH = QHBoxLayout()
#         layoutH.addLayout(layoutV)
#         layoutH.addLayout(layoutVOptions)

#         self.setLayout(layoutH)

#     @property
#     def value(self):
#         return self.pollen_types

#     @value.setter
#     def value(self, value):
#         self.pollen_types = value

#     def get_pollen_types(self, listWidget):
#         return [str(listWidget.item(i).text()) for i in range(listWidget.count())]

#     def on_reset_button_click(self, listWidget):
#         listWidget.clear()
#         listWidget.addItems(self.pollen_types_original)
#         self.pollen_types = self.pollen_types_original
#         # self.value_changed.emit(text)

#     def on_remove_button_click(self, listWidget):
#         self.value_changed.emit(listWidget.selectedItems())
#         [listWidget.takeItem(listWidget.row(x)) for x in listWidget.selectedItems()]
#         self.pollen_types = self.get_pollen_types(listWidget)

#     def change_position(self, listWidget, item, mode, index, step=1):
#         currentRow = listWidget.row(item)
#         if mode == "Up":
#             if currentRow == index:
#                 return
#             currentItem = listWidget.takeItem(currentRow)
#             listWidget.insertItem(currentRow - step, currentItem)
#         elif mode == "Down":
#             items_count = listWidget.count()
#             selected_items_count = len(listWidget.selectedItems())
#             if items_count == (currentRow + selected_items_count - index):
#                 return
#             currentItem = listWidget.takeItem(currentRow)
#             listWidget.insertItem(currentRow + step, currentItem)
#         currentItem.setSelected(True)
#         self.pollen_types = self.get_pollen_types(listWidget)
#         self.value_changed.emit(self.pollen_types)

#     def on_move_up_button_click(self, listWidget):
#         [self.change_position(listWidget, x, "Up", idx) for idx, x in enumerate(listWidget.selectedItems())]

#     def on_move_down_button_click(self, listWidget):
#         selected_items = listWidget.selectedItems()
#         [self.change_position(listWidget, x, "Down", idx, step=len(selected_items)) for idx, x in enumerate(selected_items)]

#     def pollen_types_list_widget(self):
#         config = Config.get(ModelRunnerConfig)
#         listWidget = ListWidget(self)
#         for path in config.pollen_types:
#             listWidget.addItem(path);

#         listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

#         return listWidget
