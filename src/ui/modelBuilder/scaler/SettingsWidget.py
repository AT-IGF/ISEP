from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from src.common.config.configs import ModelBuilderScalerConfig
from src.common.config import Config

from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget

from src.ui.common import DirectorySelectorWidget
from src.ui.common import DirectoriesSelectorWidget
from src.ui.common.businessComponents import FilterWidget


class SettingsWidget(QWidget):
    python_files_selector = "Python files (*.py)"

    def __init__(self, signals):
        super().__init__()
        config: ModelBuilderScalerConfig = Config.get(ModelBuilderScalerConfig)
        self.scaler_name_widget = LabelValueWidget(
            "",
            config.scaler_name,
            signals,
            val_type=str,
            margins=(0, 0, 0, 0),
            suffix_label="_scaler.pkl",
        )
        self.scaler_custom_name_widget = MeasurementWidget(
            config.scaler_name != None,
            label="Scaler custom name",
            tooltip="If not set first binary directory root folder name will be taken",
            value_changed=signals.value_changed,
            children=[self.scaler_name_widget],
            margins=(0, 10, 0, 0),
        )
        self.rescale_existing_files_widget = MeasurementWidget(
            config.rescale_existing_files,
            label="Rescale existing files",
            tooltip="When scaler is fitted it creates scaled files if new files are added the old one can be rescaled.",
            value_changed=signals.value_changed,
            margins=(10, 0, 0, 0),
        )
        self.scaler_save_path_widget = DirectorySelectorWidget(
            "Scaler save path:",
            config.scaler_save_path,
            value_changed=signals.value_changed,
            show_modal=signals.show_modal,
        )
        self.filter_rel_path_widget = FilterWidget(
            filter_path=config.filter_rel_path, singals=signals
        )

        self.pollen_types_binaries_paths_widget = DirectoriesSelectorWidget(
            directories=config.pollen_types_binaries_paths, signals=signals
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.scaler_custom_name_widget)
        layoutV.addWidget(self.pollen_types_binaries_paths_widget)
        layoutV.addWidget(self.rescale_existing_files_widget)
        layoutV.addWidget(self.scaler_save_path_widget)
        layoutV.addWidget(self.filter_rel_path_widget)
        self.setLayout(layoutV)
