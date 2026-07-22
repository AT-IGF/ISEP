from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout


from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig

from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer import SettingsSignals

from src.ui.modelBuilder import supervised as supervised
from src.ui.modelBuilder import scaler as scaler
from src.ui.common import BannerWidget
from src.core import PathHelper

from src.ui.common import DirectorySelectorWidget
from src.ui.modelBuilder.common import LearningModelsWidget, ScalerWidget
from src.ui.common.businessComponents import PollenTypesWidget
from src.ui.common.businessComponents import FilterWidget


class SettigsWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    directory_value_changed = pyqtSignal(object, bool)
    run_training_value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)
    python_files_selector = "Python files (*.py)"

    def __init__(self, banner_widget: BannerWidget):
        super().__init__()
        self.config: ModelBuilderConfig = Config.get(ModelBuilderConfig)
        self.banner_widget = banner_widget
        singals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )

        self.exclude_types_widget = PollenTypesWidget(
            pollen_types=self.config.excludeTypes,
            signals=singals,
            label="Pollen types to exclude",
            include_only=[
                PollenTypesWidget.GENERAL_ALIGN_OPTION,
                PollenTypesWidget.RESET_OPTION,
                PollenTypesWidget.ADD_OPTION,
                PollenTypesWidget.REMOVE_OPTION,
                PollenTypesWidget.MOVE_OPTION,
            ],
            show_no_types_error=False,
        )
        self.learning_models_widget = LearningModelsWidget(
            learningModels=self.config.learningModels, singals=singals
        )
        self.model_save_name_widget = LabelValueWidget(
            "Train model name",
            self.config.model_save_name,
            singals,
            val_type=str,
            suffix_label=self.config.get_model_ending(),
            margins=(10, 0, 0, 0),
            requirements=["not_empty"],
        )
        self.pollen_types_cache_dir_widget = DirectorySelectorWidget(
            "Processed files cache dir",
            self.config.pollen_types_cache_rel_path,
            value_changed=self.value_changed,
            show_modal=self.show_modal,
            tooltip="Place in which train, test, validation sets will be saved.",
        )
        self.test_model_name_widget = LabelValueWidget(
            "Cache files namespace",
            self.config.test_model_name.replace("_test_model", ""),
            singals,
            tooltip="Namespace under which cache files are created in cache dir. When another models are created samples will be taken from this namespace. \
                Serves for comparison purposes between individual models.<br/><br/>\
                Files in cache dir are created in following convention: "
            + f'{"<namespace>_<pollen type>_test_reference_to_scale"}.{self.config.REFS_EXTENSION}',
            val_type=str,
            margins=(10, 10, 0, 0),
            requirements=["not_empty"],
        )
        self.train_parameters_widget = supervised.TrainParametersWidget(
            self.config.train_parameters, singals
        )

        self.scaler_widget = ScalerWidget(
            scaler_path=self.config.scaler_path,
            value_changed=self.value_changed,
            show_modal=self.show_modal,
            banner_widget=banner_widget,
            margins=(0, 10, 0, 0),
        )
        self.filter_rel_path_widget = FilterWidget(
            filter_path=self.config.filter_rel_path, singals=singals
        )
        self.run_training_widget = MeasurementWidget(
            self.config.run_training,
            label="Run training",
            tooltip="",
            value_changed=self.run_training_value_changed,
            children=[
                self.pollen_types_cache_dir_widget,
                self.test_model_name_widget,
                self.exclude_types_widget,
                self.learning_models_widget,
                self.scaler_widget,
                self.filter_rel_path_widget,
                self.train_parameters_widget,
            ],
            layout="Vertical",
            margins=(10, 10, 0, 0),
        )

        self.run_training_value_changed.connect(
            lambda obj, changed: self.banner_widget.show_hide_whole_banner(
                is_visible=self.run_training_widget.value
            )
        )

        self.run_training_value_changed.connect(
            lambda obj, changed: self.value_changed.emit(obj, changed)
        )

        def get_model_exists_message():
            model_path = Path(
                self.config.get_model_path(
                    model_save_name=self.model_save_name_widget.value
                )
            )
            return f"'{model_path.name}' - model under this name already exists. Will be overwritten."

        self.model_save_name_widget.value_changed.connect(
            lambda obj, changed: self.show_banner_if_model_exists(
                self.model_save_name_widget,
                is_selected=self.run_training_widget.value,
                message=get_model_exists_message(),
            )
        )
        self.show_banner_if_model_exists(
            self.model_save_name_widget,
            is_selected=self.config.run_training,
            message=get_model_exists_message(),
        )

        def get_model_not_exists_message():
            return f"Reference namespace does not exists. To create it 'Train model name' and 'Cache files namespace' must be equal"

        self.test_model_name_widget.editingFinished.connect(
            lambda _: self.show_banner_if_reference_not_exists(
                self.test_model_name_widget,
                is_selected=self.run_training_widget.value,
                message=get_model_not_exists_message(),
            )
        )
        self.show_banner_if_reference_not_exists(
            self.test_model_name_widget,
            is_selected=self.run_training_widget.value,
            message=get_model_not_exists_message(),
        )

        layoutV = QVBoxLayout()
        layoutV.setSpacing(0)
        layoutV.addWidget(self.model_save_name_widget)
        layoutV.addWidget(self.run_training_widget)
        layoutV.addStretch()
        # layoutV.setSizeConstraint(QLayout.SetMinimumSize)

        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    def show_banner_if_model_exists(self, obj, is_selected, message=None):
        path = self.config.get_model_path(self.model_save_name_widget.value)
        is_file_exists = PathHelper.is_file_exists(path)
        if not is_selected or not is_file_exists:
            self.banner_widget.show_hide_banner(obj, False, None)
            return

        self.banner_widget.show_hide_banner(obj, is_file_exists, message)

    def show_banner_if_reference_not_exists(self, obj, is_selected, message=None):
        from src.modelBuilder.datasetHandler import DatasetScaler
        from src.modelBuilder.ModelBuilder import get_raw_data_types

        binary_dirs = get_raw_data_types()
        is_all_exists = True
        for binary_dir in binary_dirs:
            path = self.config.get_test_reference_file_path(
                binary_dir_path=binary_dir,
                test_model_name=self.test_model_name_widget.value,
                suffix=DatasetScaler.file_to_scale_suffix,
            )
            is_file_exists = PathHelper.is_file_exists(path)
            if not is_file_exists:
                is_all_exists = False
                break
        if (
            not is_all_exists
            and self.model_save_name_widget.value != self.test_model_name_widget.value
        ):
            self.banner_widget.show_hide_banner(obj, True, message)
            return
        self.banner_widget.show_hide_banner(obj, False, None)
