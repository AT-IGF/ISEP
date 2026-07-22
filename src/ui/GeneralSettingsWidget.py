from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QVBoxLayout,
    QLabel,
)


from src.common import Consts
from src.common.config import Config
from src.common.config.configs import TypesConfig, PathsConfig

from src.ui.common.SubmitWidget import SubmitWidget
from src.ui.common.signals import signal_bus
from src.ui.dataViewer import Signal, SettingsSignals
import matplotlib


from src.ui.common import DirectorySelectorWidget
from src.ui.common.businessComponents import PollenTypesWidget

matplotlib.use("Qt5Agg")


class GeneralSettingsWidget(QWidget):
    paths_changed = pyqtSignal(object, bool)
    types_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)

    def __init__(self, parent):
        super(GeneralSettingsWidget, self).__init__(parent)
        relative_path_widget = QLabel(f"Resources path: {Consts.RESOURCES_PATH}")
        relative_path_widget.setIndent(10)

        path_config: PathsConfig = Config.get(PathsConfig)
        paths_widget = DirectorySelectorWidget(
            label="Zip files path",
            init_path=path_config.zip_files_rel_path,
            value_changed=self.paths_changed,
            show_modal=self.show_modal,
            align=None,
            tooltip="Path in which labeled pollen types are located. It should contain sub-folders that will be treated as labels. Every subfolder should contain binary measurements from the E-Rapid.",
        )

        def get_path_config_callback():
            return self.get_paths_config(paths_widget)

        paths_submit_widget = SubmitWidget(
            config=path_config,
            config_callback=get_path_config_callback,
            on_run_click=None,
            overwrite_btn_text="Overwrite zip files paths",
        )
        paths_submit_widget.on_save_signal.connect(
            lambda: signal_bus.path_changed.emit(paths_widget.value)
        )

        path_signal = Signal(value=paths_widget.value, value_changed=self.paths_changed)
        types_config: TypesConfig = Config.get(TypesConfig)
        types_singals = SettingsSignals(
            value_changed=self.types_changed, show_modal=self.show_modal
        )
        types_widget = PollenTypesWidget(
            pollen_types=types_config.pollen_types,
            signals=types_singals,
            path_signal=path_signal,
            general_config_mismatch_warning=False,
        )

        def get_types_config_callback():
            return self.get_types_config(types_widget)

        types_submit_widget = SubmitWidget(
            config=types_config,
            config_callback=get_types_config_callback,
            on_run_click=None,
            overwrite_btn_text="Overwrite pollen types",
        )
        types_submit_widget.on_save_signal.connect(
            lambda: signal_bus.general_types_saved.emit(types_widget.get_types())
        )

        self.paths_changed.connect(
            lambda obj, is_changed: paths_submit_widget.on_form_change(obj, is_changed)
        )
        self.types_changed.connect(
            lambda obj, is_changed: types_submit_widget.on_form_change(obj, is_changed)
        )
        self.show_modal.connect(lambda x: self.show_modal_fn(x))

        widgets = [
            relative_path_widget,
            paths_widget,
            types_widget,
            paths_submit_widget,
            types_submit_widget,
        ]

        self.layout = QVBoxLayout(self)
        [self.layout.addWidget(widget) for widget in widgets]
        self.layout.addStretch()
        self.setLayout(self.layout)

    def show_modal_fn(self, message: str):
        QMessageBox.critical(self, "Error", message)

    def get_types_config(self, types_widget: PollenTypesWidget):
        new_config = TypesConfig(types_widget.get_types())

        return new_config

    def get_paths_config(self, save_directory_widget: DirectorySelectorWidget):
        new_config = PathsConfig(zip_files_rel_path=save_directory_widget.value)

        return new_config
