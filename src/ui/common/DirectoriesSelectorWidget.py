from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QAbstractItemView,
    QListWidget,
)

import copy
from src.common import Consts
from src.ui.dataViewer import SettingsSignals, Signal
import src.ui.common.Messages as messages
from src.ui.common import IconLabel

from src.ui.common.buttons import (
    RemoveButtonWidget,
    MoveButtonWidget,
    ResetButtonWidget,
)
from src.ui.common import DirectorySelectorWidget


def get_directories(listWidget):
    return [str(listWidget.item(i).text()) for i in range(listWidget.count())]


class AddButtonWidget(QWidget):
    value_changed = pyqtSignal(object, bool)

    def __init__(self, types_signal: Signal, listWidget, show_modal, button_width=None):
        super().__init__()
        self.show_modal = show_modal
        self.value_original = copy.deepcopy(types_signal.value)
        self.value_changed_signal = types_signal.value_changed

        self.directory_selector_widget = DirectorySelectorWidget(
            label=None,
            init_path=types_signal.value,
            value_changed=self.value_changed,
            show_modal=self.show_modal,
            button_text="Add",
            exclude_options=[DirectorySelectorWidget.EXCLUDE_ALL],
            button_width=button_width,
            margins=(0, 0, 0, 0),
        )
        self.value_changed.connect(
            lambda widget, is_changed: self.on_click(widget.value, listWidget)
        )

        layoutH = QVBoxLayout()
        layoutH.addWidget(self.directory_selector_widget)
        layoutH.setContentsMargins(0, 25, 0, 0)  # left, top, right, bottom
        self.setLayout(layoutH)

    def on_click(self, value: str, listWidget: list[str]):
        current_directories = get_directories(listWidget)
        dir = value.strip()
        dir = self.get_display_text(dir)
        if dir == "":
            self.show_modal.emit(messages.EMPYT_STRING_ERROR)
            return
        if dir in current_directories:
            self.show_modal.emit(messages.ITEM_ALREADY_EXISTS_ERROR)
            return

        listWidget.addItem(dir)
        self.value_changed_signal.emit(get_directories(listWidget))
        self.value = get_directories(listWidget)

    def get_display_text(self, path):
        if path == None:
            return ""
        if isinstance(path, str):
            return path.replace(Consts.RESOURCES_PATH + "/", "")
        else:
            return path


class DirectoriesSelectorWidget(QWidget):
    value_changed = pyqtSignal(object)
    show_modal = pyqtSignal(object)

    RESET_OPTION = "RESET"
    ADD_OPTION = "ADD"
    REMOVE_OPTION = "REMOVE"
    MOVE_OPTION = "MOVE"

    OPTIONS = [RESET_OPTION, ADD_OPTION, REMOVE_OPTION, MOVE_OPTION]

    def __init__(
        self,
        directories,
        label="Directories",
        signals: SettingsSignals = None,
        include_only=None,
        tooltip="Directory on which scaler will be created.\
            </br><b>Note</b>: best to use desired dataset on which trained model will be used - set used in Model runner tab.",
    ):
        super().__init__()
        label = QLabel(label)
        directories_help = IconLabel(
            "mdi.help-circle-outline", tooltip=tooltip, color="darkBlue"
        )
        self.listWidget = self.directories_list_widget(directories)
        self._value = get_directories(self.listWidget)
        self.value_original = get_directories(self.listWidget)
        types_signal = Signal(value=self.value, value_changed=self.value_changed)
        layoutV = QVBoxLayout()
        layoutH = QHBoxLayout()
        layoutH.addWidget(label)
        layoutH.addWidget(directories_help)
        layoutV.addLayout(layoutH)
        layoutV.addWidget(self.listWidget)

        if signals != None:
            self.value_changed.connect(
                lambda value: signals.value_changed.emit(
                    self, value != self.value_original
                )
            )
            self.show_modal.connect(lambda msg: signals.show_modal.emit(msg))

        def update_icon_state(is_combined_enabled: bool):
            if is_combined_enabled:
                self.file_exists_warning_icon.hide()
            else:
                self.update_tooltip(self.listWidget)

        self.update_icon_state = update_icon_state

        reset_button = ResetButtonWidget(
            types_signal=types_signal, listWidget=self.listWidget, width=100
        )
        add_button = AddButtonWidget(
            types_signal=types_signal,
            listWidget=self.listWidget,
            show_modal=self.show_modal,
            button_width=100,
        )
        remove_button = RemoveButtonWidget(
            types_signal=types_signal, listWidget=self.listWidget, width=100
        )
        move_up_button = MoveButtonWidget(
            types_signal=types_signal, listWidget=self.listWidget, mode="Up", width=100
        )
        move_down_button = MoveButtonWidget(
            types_signal=types_signal,
            listWidget=self.listWidget,
            mode="Down",
            width=100,
        )

        layoutVOptions = QVBoxLayout()
        if include_only is None or self.ADD_OPTION in include_only:
            layoutVOptions.addWidget(add_button)
        if include_only is None or self.REMOVE_OPTION in include_only:
            layoutVOptions.addWidget(remove_button)
        if include_only is None or self.MOVE_OPTION in include_only:
            layoutVOptions.addWidget(move_up_button)
            layoutVOptions.addWidget(move_down_button)
        if include_only is None or self.RESET_OPTION in include_only:
            layoutVOptions.addWidget(reset_button)
        layoutVOptions.addStretch(0)
        layoutVOptions.setContentsMargins(0, 0, 0, 0)

        self.value_changed.connect(lambda value: self.on_value_change(value))

        layoutH = QHBoxLayout()
        layoutH.addLayout(layoutV, stretch=1)
        layoutH.addLayout(layoutVOptions, stretch=0)

        self.setLayout(layoutH)

    def on_value_change(self, value):
        self.value = value

    @property
    def value(self):
        return get_directories(self.listWidget)

    @value.setter
    def value(self, value):
        self._value = value

    def directories_list_widget(self, directories):
        listWidget = QListWidget(self)
        for path in directories:
            listWidget.addItem(path)

        listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        return listWidget
