import logging
from PyQt5.QtCore import pyqtSignal, Qt, QUrl
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QSizePolicy,
)
from PyQt5.QtGui import QDesktopServices, QIcon

import os
import subprocess
from src.core import PathHelper

from src.common import Consts
from src.common.config import Config
from src.common.config.configs import PathsConfig

from src.ui.common.FieldsHelper import is_valid_path
import matplotlib


import src.ui.common.Messages as messages
from src.ui.common import IconLabel
from src.ui.common.Helpers.TooltipHelper import add_tooltip_or_text_to_layout
from src.core import is_blank
from src.ui.common import BannerWidget

matplotlib.use("Qt5Agg")


class DirectorySelectorWidget(QWidget):
    value_changed = pyqtSignal(object)
    show_modal = pyqtSignal(object)

    EXTENSION_SEPARATOR = ";;"

    JOBLIB_FILE_EXTENSION = "Joblib files (*.joblib)"
    JSON_FILE_EXTENSION = "Json files (*.json)"
    CSV_FILE_EXTENSION = "CSV files (*.csv)"
    KERAS_EXTENSION = "Keras files (*.keras)"
    H5_EXTENSION = "HDF5 files (*.h5)"
    PICKLE_EXTENSION = "Pickle files (*.pkl)"
    SCALER_EXTENSION = "Scaler files (*_scaler.pkl)"
    TF_MODEL_EXTENSION = "Tensorflow models (*.h5 *keras)"

    REST_BUTTON = "RESET_BUTTON"
    EXPLORER_BUTTON = "EXPLORER_BUTTON"
    EXCLUDE_ALL = "EXCLUDE_ALL"

    OPTIONS = [REST_BUTTON, EXPLORER_BUTTON]

    def __init__(
        self,
        label,
        init_path,
        value_changed=None,
        show_modal=None,
        default_path=Consts.RESOURCES_PATH,
        selector="DIRECTORY",
        extensions: str | None = None,
        display_text=None,
        tooltip=None,
        margins=None,
        align="LEFT",
        exclude_options=[],
        button_text=None,
        button_width=None,
        banner: tuple[BannerWidget, str] | None = None,
    ):
        super().__init__()
        layoutH = QHBoxLayout()
        self.selector = selector
        self.display_text = display_text
        self.extensions = extensions
        if default_path == None:
            raise ValueError("Default path cannot be None")
        self.default_path = default_path

        self._value = init_path
        self._value_original = init_path

        if value_changed != None:
            self.value_changed.connect(
                lambda path: value_changed.emit(self, path != self._value_original)
            )

        if show_modal != None:
            self.show_modal = show_modal

        self.button_text = button_text
        btn_text = self.get_display_text(self._value)
        if button_text != None:
            btn_text = button_text

        select_model_button = QPushButton(btn_text)
        if isinstance(self._value, str):
            select_model_button.setToolTip(self.get_path(self._value))
        select_model_button.clicked.connect(
            lambda: self.on_button_click(select_model_button)
        )
        if isinstance(button_width, int):
            select_model_button.setMinimumWidth(button_width)
        elif button_width == "FULL_WIDTH":
            select_model_button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Preferred  # horizontal
            )
        else:
            select_model_button.setMinimumWidth(250)

        if not is_blank(label):
            label_widget = QLabel(label)
            layoutH.addWidget(label_widget)

            add_tooltip_or_text_to_layout(
                tooltip=tooltip,
                label_widget=label_widget,
                layout=layoutH,
                spacer=True,
            )

        layoutH.addWidget(select_model_button)

        is_exclude_all = self.EXCLUDE_ALL in exclude_options
        if self.REST_BUTTON not in exclude_options and not is_exclude_all:
            reset_button = QPushButton("⟳")
            reset_button.setToolTip("reset")
            reset_button.clicked.connect(
                lambda: self.reset_button_click(path_button=select_model_button)
            )
            reset_button.setFixedWidth(50)
            reset_button.setEnabled(False)
            self.value_changed.connect(
                lambda path: reset_button.setEnabled(path != self._value_original)
            )
            layoutH.addWidget(reset_button)

        if self.EXPLORER_BUTTON not in exclude_options and not is_exclude_all:
            open_in_explorer_icon = QPushButton()
            open_in_explorer_icon.setToolTip("open in new window")
            open_in_explorer_icon.setIcon(
                QIcon(
                    PathHelper.join_path(
                        Consts.RESOURCES_PATH, "ui/icons/open-in-new-window-24.png"
                    )
                )
            )
            open_in_explorer_icon.setFixedWidth(50)

            open_in_explorer_icon.clicked.connect(self.open_in_explorer)
            layoutH.addWidget(open_in_explorer_icon)

        if margins != None:
            layoutH.setContentsMargins(*margins)  # left, top, right, bottom
        if align == "LEFT":
            layoutH.setAlignment(Qt.AlignLeft)

        if banner is not None:
            self.show_hide_model_path_banner(banner)

        layoutH.addStretch(1)
        self.setLayout(layoutH)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value != value:
            self._value = value
            self.value_changed.emit(self._value)

    def get_path(self, path):
        if not isinstance(path, str):
            return Consts.RESOURCES_PATH

        current_path = path
        if PathHelper.is_rel_path(path):
            current_path = PathHelper.get_absolute_path(
                Consts.RESOURCES_PATH, path, raise_on_not_found=False
            )
        return current_path

    def get_dir(self, path):
        path = self.get_path(path)
        if PathHelper.is_file(path):
            return PathHelper.get_dirs(path)
        return path

    def get_display_text(self, path):
        if self.display_text is not None:
            return self.display_text
        if path == None:
            return ""
        if isinstance(path, str):
            return path.replace(Consts.RESOURCES_PATH + "/", "")
        else:
            return "Select"

    def on_button_click(self, button):
        if self.value == None:
            current_dir = self.default_path
        else:
            current_dir = self.get_dir(self.value)
        if not PathHelper.is_dir_exists(current_dir):
            current_dir = Consts.RESOURCES_PATH

        if self.selector == "FILE":
            extensions = self.extensions
            if isinstance(self.extensions, list):
                extensions = self.EXTENSION_SEPARATOR.join(self.extensions)

            if not is_blank(extensions) and not extensions.endswith(
                self.EXTENSION_SEPARATOR
            ):
                extensions += self.EXTENSION_SEPARATOR

            directory, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Select a filter",
                directory=current_dir,
                filter=f"{extensions}All Files (*)",
                options=QFileDialog.Options(),
            )
        else:
            directory = QFileDialog.getExistingDirectory(
                self, "Select directory", current_dir
            )
        if directory == "":
            return
        if not is_valid_path(directory):
            self.show_modal.emit(messages.RELATIVE_PATH_ERROR)
            return
        directory_display = self.get_display_text(directory)
        self._value = directory
        if self.button_text == None:
            button.setText(str(directory_display))
            button.setToolTip(directory)
        self.value_changed.emit(str(directory))

    def reset_button_click(self, path_button):
        self.value = self._value_original
        directory_display = self.get_display_text(self._value_original)
        if self.button_text == None:
            path_button.setText(str(directory_display))
        self.value_changed.emit(self.value)

    def is_wsl(self):
        try:
            with open("/proc/version", "r") as f:
                return "microsoft" in f.read().lower()
        except Exception:
            return False

    def get_folder_to_open(self, path):
        if os.path.isfile(path):
            return PathHelper.get_dirs(path)
        return path

    def open_in_explorer(self):
        path = self.get_path(self.value)
        path = self.get_folder_to_open(path)

        if not PathHelper.is_file_exists(path) or not PathHelper.is_dir_exists(path):
            self.show_modal.emit("Path does not exists")

        if self.is_wsl():
            try:
                completed = subprocess.run(
                    ["wslpath", "-w", path], capture_output=True, text=True, check=True
                )
                win_path = completed.stdout.strip()
                subprocess.run(["explorer.exe", win_path])
            except Exception as e:
                print("Failed to open in Explorer via WSL2:", e)
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def show_hide_model_path_banner(
        self,
        banner: tuple[BannerWidget, str],
    ):
        banner_widget, text = banner

        def show_hide(path):
            is_path_exists = PathHelper.is_file(path)
            banner_widget.show_hide_banner(
                self,
                is_visible=not is_path_exists,
                text=text,
            )

        self.value_changed.connect(lambda path: show_hide(path))

        show_hide(self.value)
