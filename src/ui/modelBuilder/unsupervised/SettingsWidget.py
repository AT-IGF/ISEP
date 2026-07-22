from pathlib import Path
from signal import Signals
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from numpy import copy


from src.common.config.configs.models.modelBuilderUnsupervised import (
    TrainParametersModel,
)
from src.common.config.configs import TypesConfig
from src.common.config import Config
from src.common.config.configs import ModelBuilderUnsupervisedConfig

from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer import SettingsSignals

from src.ui.modelBuilder import scaler as scaler
from src.ui.common import BannerWidget
from src.core import PathHelper

from src.ui.common import DirectorySelectorWidget
from src.ui.modelBuilder.common import LearningModelsWidget, ScalerWidget
from src.ui.modelBuilder.unsupervised.TrainParametersWidget import TrainParametersWidget
from src.ui.common import DirectoriesSelectorWidget
from src.ui.common.businessComponents import PollenTypesWidget
import src.ui.common.types.HtmlEncoding as encoding
from src.ui.common.businessComponents import FilterWidget


class SettigsWidget(QWidget):
    value_changed_types = pyqtSignal(object, bool, object)
    show_modal = pyqtSignal(object)

    def __init__(self, singals: SettingsSignals, banner_widget: BannerWidget):
        super().__init__()
        self.config: ModelBuilderUnsupervisedConfig = Config.get(
            ModelBuilderUnsupervisedConfig
        )
        self._value = self.config.train_parameters
        self._value_original = self.config.train_parameters
        self.banner_widget = banner_widget
        self.model_save_name_widget = LabelValueWidget(
            "Train model name",
            self.config.model_save_name,
            singals=singals,
            val_type=str,
            suffix_label=self.config.get_model_ending(),
            tooltip=f"Model save name.<br/>\
                When model was already trained, the training can be continued by adding at the end _epoch{encoding.LOWER}last saved epoch{encoding.HIGHER}.\
                    Epoch progress is saved under path='unsupervised/KerasTrainer/{encoding.LOWER}model_save_name{encoding.HIGHER}', whereas final model is saved in root path.",
            requirements=["not_empty"],
        )

        self.pollen_types_cache_dir_widget = DirectorySelectorWidget(
            "Processed files cache dir:",
            self.config.train_parameters.pollen_types_cache_rel_path,
            value_changed=singals.value_changed,
            show_modal=singals.show_modal,
            tooltip="Place in which train and validation sets will be saved.<br/>\
                Cache is saved in selected filter subdir",
            margins=(10, 0, 0, 0),
        )

        self.pollen_types_binaries_paths_widget = DirectoriesSelectorWidget(
            directories=self.config.train_parameters.pollen_types_binaries_paths,
            label="Unlabeled samples directories:",
            signals=singals,
        )

        self.pollen_types_widget = PollenTypesWidget(
            self.config.train_parameters.pollen_types,
            signals=singals,
            include_only=[
                PollenTypesWidget.GENERAL_ALIGN_OPTION,
                PollenTypesWidget.ADD_OPTION,
                PollenTypesWidget.REMOVE_OPTION,
                PollenTypesWidget.MOVE_OPTION,
                PollenTypesWidget.RESET_OPTION,
            ],
        )
        pollen_types_config = Config.get(TypesConfig)
        self.pollen_types_check_widget = MeasurementWidget(
            sorted(self.config.train_parameters.pollen_types)
            == sorted(pollen_types_config.pollen_types),
            label="Types from General tab",
            tooltip="",
            value_changed=singals.value_changed,
            children=[self.pollen_types_widget],
            callbacks={self.pollen_types_widget: lambda show: not show},
            layout="Vertical",
            margins=(10, 10, 0, 0),
        )

        self.with_labeled_samples_widget = MeasurementWidget(
            self.config.train_parameters.with_labeled_samples,
            label="Dataset partially labeled",
            tooltip="When selected folders equally named as pollen types from 'General' will be used for comparison reasons",
            value_changed=singals.value_changed,
            children=[self.pollen_types_check_widget],
            layout="Vertical",
        )

        self.scaler_widget = ScalerWidget(
            scaler_path=self.config.train_parameters.scaler_path,
            value_changed=singals.value_changed,
            show_modal=self.show_modal,
            banner_widget=banner_widget,
            margins=(0, 0, 0, 0),
        )

        self.learning_models_widget = LearningModelsWidget(
            learningModels=self.config.train_parameters.learningModels, singals=singals
        )

        self.validation_set_size_widget = LabelValueWidget(
            "Validation set size",
            int(self.config.train_parameters.validation_set_size * 100),
            singals,
            val_type=int,
            suffix_label="%",
            width=50,
            tooltip=None,
            margins=(10, 10, 0, 0),
            bottom=0,
            top=100,
        )

        self.filter_rel_path_widget = FilterWidget(
            filter_path=self.config.train_parameters.filter_rel_path, singals=singals
        )
        self.train_parameters_widget = TrainParametersWidget(
            self.config.train_parameters, singals
        )
        self.run_training_widget = MeasurementWidget(
            self.config.train_parameters.train_model,
            label="Run training",
            tooltip="",
            value_changed=singals.value_changed,
            children=[
                self.pollen_types_cache_dir_widget,
                self.pollen_types_binaries_paths_widget,
                self.with_labeled_samples_widget,
                self.learning_models_widget,
                self.scaler_widget,
                self.validation_set_size_widget,
                self.filter_rel_path_widget,
                self.train_parameters_widget,
            ],
            layout="Vertical",
            margins=(0, 0, 0, 0),
            spacing_children=0,
        )

        self.run_training_widget.visibility_signal.connect(
            lambda is_visible: self.banner_widget.show_hide_whole_banner(
                is_visible=is_visible
            )
        )

        def get_model_exists_message():
            model_path = Path(
                self.config.get_model_path(
                    new_model_name=self.model_save_name_widget.value
                )
            )
            return f"'{model_path.name}' - model under this name already existst. Will be overwritten."

        self.model_save_name_widget.value_changed.connect(
            lambda obj, changed: self.show_banner_if_model_exists(
                self.model_save_name_widget,
                is_selected=self.run_training_widget.value,
                message=get_model_exists_message(),
            )
        )
        self.show_banner_if_model_exists(
            self.model_save_name_widget,
            is_selected=self.config.train_parameters.train_model,
            message=get_model_exists_message(),
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.model_save_name_widget)
        layoutV.addWidget(self.run_training_widget)
        layoutV.addStretch()
        # layoutV.setSizeConstraint(QLayout.SetMinimumSize)

        # layoutV.setSpacing(0)

        self._value_original: TrainParametersModel = self.config.train_parameters
        self._value: TrainParametersModel = self.config.train_parameters

        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    def show_banner_if_model_exists(self, obj, is_selected, message=None):
        model_path = self.config.get_model_path(
            new_model_name=self.model_save_name_widget.value
        )

        is_file_exists = PathHelper.is_file_exists(model_path)
        if (
            not is_selected
            or not is_file_exists
            or self.config.is_progress_model(
                new_model_name=self.model_save_name_widget.value
            )
        ):
            self.banner_widget.show_hide_banner(obj, False, None)
            return

        self.banner_widget.show_hide_banner(obj, is_file_exists, message)

    @property
    def value(self):
        if self.run_training_widget.value == True:
            self._value.train_model = True
            self._value.pollen_types_binaries_paths = (
                self.pollen_types_binaries_paths_widget.value
            )
            self._value.learningModels = (
                self.learning_models_widget.get_selected_values()
            )
            self._value.pollen_types = self.pollen_types_widget.value
            self._value.with_labeled_samples = self.with_labeled_samples_widget.value

            if self.with_labeled_samples_widget.value == True:
                if self.pollen_types_check_widget.value == False:
                    self._value.pollen_types = self.pollen_types_widget.get_types()
                else:
                    self._value.pollen_types = Config.get(TypesConfig).pollen_types
            else:
                self._value.pollen_types = []
                

            self._value.pollen_types_cache_rel_path = (
                self.pollen_types_cache_dir_widget.value
            )
            self._value.filter_rel_path = self.filter_rel_path_widget.value
            self._value.scaler_path = self.scaler_widget.value
            self._value.validation_set_size = (
                self.validation_set_size_widget.value / 100
            )

            self._value.epochs = self.train_parameters_widget.value.epochs
            self._value.lr = self.train_parameters_widget.value.lr
            self._value.weight_decay = self.train_parameters_widget.value.weight_decay
            self._value.early_stopping = (
                self.train_parameters_widget.value.early_stopping
            )
            self._value.lr_reducer = self.train_parameters_widget.value.lr_reducer

        else:
            self._value = self._value_original
            self._value.train_model = False
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
