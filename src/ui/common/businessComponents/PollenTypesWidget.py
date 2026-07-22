import logging
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QAbstractItemView,
    QLineEdit,
    QInputDialog,
)

from pathlib import Path
from src.core import PathHelper
import copy
from src.common.config.configs import TypesConfig, PathsConfig
from src.common import Consts
from src.common.config import Config
from src.ui.dataViewer import SettingsSignals, Signal
import src.ui.common.Messages as messages
from src.ui.common import IconLabel

from src.ui.common import BannerWidget
from src.ui.common.FieldsHelper import toogle_field_visibility
from src.ui.common.buttons import (
    RemoveButtonWidget,
    MoveButtonWidget,
    ResetButtonWidget,
)
from src.ui.common.signals import signal_bus


def get_pollen_types(listWidget):
    return [str(listWidget.item(i).text()) for i in range(listWidget.count())]


class ListWidget(QListWidget):
    def Clicked(self, item):
        QMessageBox.information(self, "ListWidget", "You clicked: " + item.text())


class GeneralAlignButton(QPushButton):
    def __init__(self, value, value_changed, listWidget):
        super().__init__()
        self.value = value
        self.value_changed = value_changed
        self.value_changed.connect(lambda value: self.set_state(value))
        signal_bus.general_types_saved.connect(lambda value: self.update_state(value))

        self.setText("Align with\ngeneral settings")
        self.clicked.connect(lambda: self.on_click(listWidget))
        self.set_state(self.value)

    def set_state(self, value):
        self.value = value
        types_config: TypesConfig = Config.get(TypesConfig)
        self.setEnabled(
            types_config.pollen_types != None and value != types_config.pollen_types
        )

    def update_state(self, value):
        self.setEnabled(self.value != value)

    def on_click(self, listWidget):
        types_config: TypesConfig = Config.get(TypesConfig)

        listWidget.clear()
        listWidget.addItems(types_config.pollen_types)
        self.value = types_config.pollen_types
        self.value_changed.emit(self.value)


class PathAlignButton(QPushButton):
    value_changed = pyqtSignal(object)

    def __init__(self, types_signal: Signal, listWidget, path_signal: Signal):
        super().__init__()
        self.pollen_types = types_signal.value
        self.on_alignment_path_change(path_signal.value)

        self.setText("Path align")
        self.clicked.connect(lambda: self.on_click(listWidget))

        types_signal.value_changed.connect(
            lambda value: self.on_pollen_type_change(value)
        )
        path_signal.value_changed.connect(
            lambda obj, is_changed: self.on_alignment_path_change(obj.value)
        )
        signal_bus.path_changed.connect(
            lambda path: self.update_path_pollen_types(path)
        )

        self.value_changed.connect(lambda value: types_signal.value_changed.emit(value))

    def path_pollen_types_callback(self):
        return self.path_pollen_types

    @property
    def path_pollen_types(self):
        return self._path_pollen_types

    @path_pollen_types.setter
    def path_pollen_types(self, value):
        self._path_pollen_types = value

    def update_path_pollen_types(self, path):
        if path == None:
            self._path_pollen_types = []
            return

        abs_path = PathHelper.join_path(Consts.RESOURCES_PATH, path)
        directory = Path(abs_path)
        subdirs = []
        if PathHelper.is_file_exists(directory):
            subdirs = [d for d in directory.iterdir() if d.is_dir()]
        if len(subdirs) == 0:
            logging.getLogger("ui").warning(
                f"No subdirs found under the path, path={path}"
            )
        pollen_types = []
        for base_dir in subdirs:
            pollen_types.append(PathHelper.get_base_name(base_dir))
        self._path_pollen_types = sorted(pollen_types)

    def on_pollen_type_change(self, value):
        self.pollen_types = value
        self.set_state()

    def on_alignment_path_change(self, value):
        self.alignment_path = value
        self.update_path_pollen_types(self.alignment_path)
        self.set_state()

    def set_state(self):
        self.setEnabled(
            self.path_pollen_types != None
            and sorted(self.pollen_types) != sorted(self.path_pollen_types)
        )

    def on_click(self, listWidget):
        if self.path_pollen_types == None:
            return

        listWidget.clear()
        listWidget.addItems(self.path_pollen_types)
        self.value_changed.emit(self.path_pollen_types)


class AddButton(QPushButton):
    value_changed = pyqtSignal(object)

    def __init__(
        self, types_signal: Signal, listWidget, allowed_names_func, show_modal
    ):
        super().__init__()
        self.allowed_names_func = allowed_names_func
        self.show_modal = show_modal
        self.value_original = copy.deepcopy(types_signal.value)

        self.setText("Add")
        self.clicked.connect(lambda: self.on_click(listWidget))
        self.value_changed.connect(lambda value: types_signal.value_changed.emit(value))

    def on_click(self, listWidget):
        text, ok_pressed = QInputDialog().getText(
            None,
            "Add particle name to predict",
            "Particle type name:",
            QLineEdit.Normal,
            "",
        )
        text = text.strip()
        current_pollen_types = get_pollen_types(listWidget)
        if ok_pressed:
            if text == "":
                self.show_modal.emit(messages.EMPYT_STRING_ERROR)
                return
            if text in current_pollen_types:
                self.show_modal.emit(messages.ITEM_ALREADY_EXISTS_ERROR)
                return
            path_pollen_types = self.allowed_names_func()
            if text not in path_pollen_types:
                diff_types = [
                    x for x in path_pollen_types if x not in current_pollen_types
                ]
                found_message = ""
                if len(diff_types) > 0:
                    found_message = f"\n\nFound values:\n{', '.join(diff_types)}"
                result = self.showDialog(
                    f"'{text}' not found under zip files subdir.{found_message}\n\nContinue?"
                )
                if result == False:
                    return

            listWidget.addItem(text)
            self.value_changed.emit(get_pollen_types(listWidget))
        self.value = get_pollen_types(listWidget)

    def showDialog(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle("Confirm")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            return True
        return False


class PollenTypesWidget(QWidget):
    value_changed = pyqtSignal(object)
    show_modal = pyqtSignal(object)
    paths_changed = pyqtSignal(object, bool, object)

    TOOLTIP_MESSAGE_DEFAULT = "Particle type names that model will be predicting.<br/><br/><b>Note: when using a trained model, the count and order in this list must be the same as when model was trained.<b/>"

    GENERAL_ALIGN_OPTION = "GENERAL_ALIGN"
    PATH_ALIGN_OPTION = "PATH_ALIGN"
    RESET_OPTION = "RESET"
    ADD_OPTION = "ADD"
    REMOVE_OPTION = "REMOVE"
    MOVE_OPTION = "MOVE"

    OPTIONS = [
        GENERAL_ALIGN_OPTION,
        PATH_ALIGN_OPTION,
        RESET_OPTION,
        ADD_OPTION,
        REMOVE_OPTION,
        MOVE_OPTION,
    ]

    def __init__(
        self,
        pollen_types,
        pollen_types_to_exclude=None,
        signals: SettingsSignals = None,
        path_signal: Signal = None,
        include_only=None,
        show_no_types_error=True,
        label="Pollen types",
        tooltip=TOOLTIP_MESSAGE_DEFAULT,
        margins=None,
        general_config_mismatch_warning=True,
    ):
        super().__init__()
        label = QLabel(label)
        pollen_types_help = IconLabel(
            "mdi.help-circle-outline", tooltip=tooltip, color="darkBlue"
        )
        if pollen_types_to_exclude != None:
            pollen_types = [x for x in pollen_types if x not in pollen_types_to_exclude]
        listWidget = self.pollen_types_list_widget(pollen_types)
        self.show_no_types_error = show_no_types_error
        self._value = get_pollen_types(listWidget)
        self.value_original = get_pollen_types(listWidget)
        self.general_config_mismatch_warning = general_config_mismatch_warning
        types_signal = Signal(value=self.value, value_changed=self.value_changed)

        layoutV = QVBoxLayout()
        layoutH = QHBoxLayout()
        layoutH.addWidget(label)
        layoutH.addWidget(pollen_types_help)
        layoutV.addLayout(layoutH)
        layoutV.addWidget(listWidget)

        def get_types():
            return get_pollen_types(listWidget)

        self.get_types = get_types

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
                self.update_tooltip(listWidget)

        self.update_icon_state = update_icon_state

        layoutVOptions = QVBoxLayout()

        if path_signal == None:
            path_config: PathsConfig = Config.get(PathsConfig)
            path_signal = Signal(
                value=path_config.zip_files_rel_path, value_changed=self.paths_changed
            )

        general_align_button = GeneralAlignButton(
            value=self.value, value_changed=self.value_changed, listWidget=listWidget
        )
        path_align_button = PathAlignButton(
            types_signal=types_signal, listWidget=listWidget, path_signal=path_signal
        )
        reset_button = ResetButtonWidget(
            types_signal=types_signal, listWidget=listWidget
        )
        add_button = AddButton(
            types_signal=types_signal,
            listWidget=listWidget,
            allowed_names_func=path_align_button.path_pollen_types_callback,
            show_modal=self.show_modal,
        )
        remove_button = RemoveButtonWidget(
            types_signal=types_signal, listWidget=listWidget
        )
        move_up_button = MoveButtonWidget(
            types_signal=types_signal, listWidget=listWidget, mode="Up"
        )
        move_down_button = MoveButtonWidget(
            types_signal=types_signal, listWidget=listWidget, mode="Down"
        )

        if include_only is None or self.GENERAL_ALIGN_OPTION in include_only:
            layoutVOptions.addWidget(general_align_button)
        if include_only is None or self.PATH_ALIGN_OPTION in include_only:
            layoutVOptions.addWidget(path_align_button)
        if include_only is None or self.ADD_OPTION in include_only:
            layoutVOptions.addWidget(add_button)
        if include_only is None or self.REMOVE_OPTION in include_only:
            layoutVOptions.addWidget(remove_button)
        if include_only is None or self.MOVE_OPTION in include_only:
            layoutVOptions.addWidget(move_up_button)
            layoutVOptions.addWidget(move_down_button)
        if include_only is None or self.RESET_OPTION in include_only:
            layoutVOptions.addWidget(reset_button)
        layoutVOptions.setAlignment(Qt.AlignCenter)

        self.value_changed.connect(lambda value: self.on_value_change(value))

        mismatch_warning = BannerWidget(type="Warning")
        self.handle_warning(
            self.get_types(),
            mismatch_warning,
            path_align_button.path_pollen_types_callback,
        )
        self.value_changed.connect(
            lambda _: self.handle_warning(
                self.get_types(),
                mismatch_warning,
                path_align_button.path_pollen_types_callback,
            )
        )
        path_signal.value_changed.connect(
            lambda: self.handle_warning(
                self.get_types(),
                mismatch_warning,
                path_align_button.path_pollen_types_callback,
            )
        )
        signal_bus.path_changed.connect(
            lambda: self.handle_warning(
                self.get_types(),
                mismatch_warning,
                path_align_button.path_pollen_types_callback,
            )
        )

        signal_bus.general_types_saved.connect(
            lambda types: self.handle_warning(
                types,
                mismatch_warning,
                path_align_button.path_pollen_types_callback,
            )
        )

        layoutV_all = QVBoxLayout()
        layoutH = QHBoxLayout()
        layoutH.addLayout(layoutV)
        layoutH.addLayout(layoutVOptions)
        layoutV_all.addLayout(layoutH)
        layoutV_all.addWidget(mismatch_warning)
        if margins != None:
            layoutV_all.setContentsMargins(*margins)

        self.setLayout(layoutV_all)

    def on_value_change(self, value):
        self.value = value

    def get_missing_zip_path_types(self, types, allowed_names_func):
        path_pollen_types = [types] if isinstance(types, str) else types
        current_pollen_types = allowed_names_func()
        diff_types = [x for x in path_pollen_types if x not in current_pollen_types]
        return diff_types

    def get_irrelevant_pollen_types(self, types, mismatch_types):
        list_pollen_types = [types] if isinstance(types, str) else types
        types_config: TypesConfig = Config.get(TypesConfig)
        diff_types = [
            x
            for x in list_pollen_types
            if x not in types_config.pollen_types and x not in mismatch_types
        ]
        return diff_types

    def handle_warning(self, types, widget: BannerWidget, allowed_names_func):
        widget.show_hide_banner(
            "1",
            len(types) == 0 and self.show_no_types_error == True,
            "No pollen types is set.\nThis state will cause improper program behavior.",
        )

        mismatch_types = self.get_missing_zip_path_types(types, allowed_names_func)
        widget.show_hide_banner(
            "2",
            len(mismatch_types) != 0,
            f"Pollen types are not aligned with the zip files path.\nThis can cause improper program behavior.\nMismatch types:\n{', '.join(mismatch_types)}",
        )

        if self.general_config_mismatch_warning:
            irrelevant_pollen_types = self.get_irrelevant_pollen_types(
                types, mismatch_types
            )
            widget.show_hide_banner(
                "3",
                len(irrelevant_pollen_types) != 0,
                f"No pollen type is not set in pollen type general config.\nExclusion of it will not take affect.\nIrrelevant pollen types:\n{', '.join(irrelevant_pollen_types)}",
            )

    def is_subdir_match(self, subdir_types, widget_types):
        return sorted(subdir_types) == sorted(widget_types)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def get_pollen_types_to_exclude(self):
        types_config: TypesConfig = Config.get(TypesConfig)
        return [x for x in types_config.pollen_types if x not in self.value]

    def pollen_types_list_widget(self, pollen_types):
        listWidget = ListWidget(self)
        for path in pollen_types:
            listWidget.addItem(path)

        listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        return listWidget
