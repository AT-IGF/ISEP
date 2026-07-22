from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLayout, QLabel


from src.common import Consts
from src.common.config.configs.models.modelBuilder import CalibrationModel
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig

from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.common.FieldsHelper import scroll_to_element
from src.ui.dataViewer import SettingsSignals

from src.ui.modelBuilder import supervised as supervised
from src.ui.modelBuilder import scaler as scaler

from src.ui.common import SectionWidget
from src.ui.common.types import Messages as messages
from src.core import PathHelper

from src.ui.common import LayoutWidget
from src.ui.dataViewer.aggregatedSamples.AggregatorWidget import (
    Radio,
    RadioSelectorWidget,
)


class CalibrationWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)
    modify_defaults_value_changed = pyqtSignal(object, bool)
    calibration_widget_value_changed = pyqtSignal(object, bool)

    def __init__(self, banner_signal, scroll, model_name_signal):
        super().__init__()
        config_base: ModelBuilderConfig = Config.get(ModelBuilderConfig)
        self.config: CalibrationModel = config_base.calibration
        singals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )

        calibrated_model_name = self.get_calibrated_model_name()
        calibrated_model_name_widget = LabelValueWidget(
            value=calibrated_model_name,
            label="Calib. model name",
            singals=singals,
            tooltip="Calibrated model save name",
            val_type=str,
            read_only=True,
            suffix_label=f".{ModelBuilderConfig.KERAS_EXTENSION}",
            margins=(0, 0, 0, 0),
        )
        self.overwrite_model_widget = MeasurementWidget(
            self.config.overwrite_model,
            label="Overwrite if exists",
            tooltip="",
            value_changed=singals.value_changed,
            margins=(5, 0, 0, 0),
        )

        model_name_layout_widget = LayoutWidget(
            children=[calibrated_model_name_widget, self.overwrite_model_widget],
            margins=(10, 0, 0, 0),
        )
        model_name_signal.connect(
            lambda val: calibrated_model_name_widget.setText(
                self.get_calibrated_model_name(val)
            )
        )

        evaluation_apps = [
            Radio(
                value=self.config.CLASS_EVALUATION,
                selected_value=self.config.evaluation_mode,
                label="Class wise",
            ),
            Radio(
                value=self.config.ALL_EVALUATION,
                selected_value=self.config.evaluation_mode,
                label="Top label",
            ),
        ]

        self.evaluation_mode_widget = RadioSelectorWidget(
            self,
            evaluation_apps,
            singals.value_changed,
            label="Mode:",
            layout="Horizontal",
            margins=(0, 0, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Inline",
        )

        self.evaluate_calibration_widget = MeasurementWidget(
            self.config.evaluate_calibration,
            label="Evaluate calibration",
            tooltip="Divides model into bins, shows what model predicted (acc) and in what was the ratio of true labels (conf)<br/>\
                E.g. acc = 0.35 conf = 0.4. Model is underconfident.<br/>\
                Class wise - what accuracy for specific label confidence<br/>\
                Top label - what accuracy for top label confidence",
            value_changed=singals.value_changed,
            children=[self.evaluation_mode_widget],
        )

        reliability_apps = [
            Radio(
                value=self.config.CLASS_EVALUATION,
                selected_value=self.config.reliability_mode,
                label="Class wise",
            ),
            Radio(
                value=self.config.ALL_EVALUATION,
                selected_value=self.config.reliability_mode,
                label="Top label",
            ),
        ]

        self.reliability_mode_widget = RadioSelectorWidget(
            self,
            reliability_apps,
            singals.value_changed,
            label="Mode:",
            layout="Horizontal",
            margins=(0, 0, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Inline",
        )

        self.plot_reliability_curves_widget = MeasurementWidget(
            self.config.plot_reliability_curves,
            label="Plot reliability curves",
            tooltip="Indicates how reliable the model is. If below XY line - underconfident, above - overconfident.<br/><br/>\
                Class wise - plots for every class. How reliable is particular class prediction.<br/>\
                Top label - selected class with the highest prediction",
            children=[self.reliability_mode_widget],
            value_changed=singals.value_changed,
        )
        self.plot_temp_changes_widget = MeasurementWidget(
            self.config.plot_temp_changes,
            label="Plot temperature changes",
            tooltip="Plots temperature changes during training",
            value_changed=singals.value_changed,
        )
        self.plot_probability_distributions_widget = MeasurementWidget(
            self.config.plot_probability_distributions,
            label="Plot probability distributions",
            tooltip="Shows how max label probabilities are distributed before and after calibration.<br/>\
                With the rule of thumb: more samples to the right the better<br/>\
                Note: probabilities not accuracies. Model can state all the time sure no 1 but predict wrong",
            value_changed=singals.value_changed,
        )

        self.general_section_widget = SectionWidget("General")
        self.epochs_widget = LabelValueWidget(
            value=self.config.epochs,
            label="Epochs",
            singals=singals,
            tooltip=messages.EPOCHS_TRAIN_PARAMS_TEXT,
            val_type=int,
            bottom=0,
            top=Consts.INT_MAX,
            margins=(20, 10, 0, 0),
        )
        self.lr_widget = LabelValueWidget(
            value=self.config.lr,
            label="Learning rate",
            singals=singals,
            tooltip=messages.LR_TRAIN_PARAMS_TEXT,
            val_type=float,
            bottom=0,
            top=1,
            decimals=2,
            margins=(20, 10, 0, 0),
        )
        modify_defaults = False
        self.modify_training_defaults = MeasurementWidget(
            modify_defaults,
            label="Modify training default parameters",
            tooltip="",
            value_changed=self.modify_defaults_value_changed,
            children=[
                self.general_section_widget,
                self.epochs_widget,
                self.lr_widget,
            ],
            layout="Vertical",
        )

        self.calibration_widget = MeasurementWidget(
            self.config.run_calibration,
            label="Run calibration",
            tooltip="Calibrate trained model with the use of temperature scaling regularization technique. Takes output logits and with the use of neural network align the weights.",
            value_changed=self.calibration_widget_value_changed,
            children=[
                model_name_layout_widget,
                self.evaluate_calibration_widget,
                self.plot_reliability_curves_widget,
                self.plot_temp_changes_widget,
                self.plot_probability_distributions_widget,
                self.modify_training_defaults,
            ],
            layout="Vertical",
        )
        self.calibration_widget_value_changed.connect(
            lambda obj, is_changed: self.set_banner_visibility(banner_signal)
        )
        self.calibration_widget_value_changed.connect(
            lambda obj, changed: scroll_to_element(
                self, scroll, self.calibration_widget.value
            )
        )

        self.calibration_widget_value_changed.connect(
            lambda obj, changed: self.value_changed.emit(obj, changed)
        )

        self.set_banner_visibility(banner_signal)

        self._value = CalibrationModel(**self.config.__dict__)
        self.value_original = CalibrationModel(**self.config.__dict__)

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.calibration_widget)
        layoutV.setAlignment(Qt.AlignTop)
        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        layoutV.setSizeConstraint(QLayout.SetMinimumSize)

    def set_banner_visibility(self, banner_signal):
        banner_signal.emit(
            self.calibration_widget,
            self.calibration_widget.value,
            "Calibration is enabled, summaries will be shown for the calibrated model",
        )

    def get_calibrated_model_name(self, value=None):
        config_base = Config.get(ModelBuilderConfig)

        return PathHelper.get_filename(
            config_base.get_calibrated_model_path(model_save_name=value)
        )

    @property
    def value(self):
        if self.calibration_widget.value == True:
            self._value.run_calibration = True
            self._value.overwrite_model = self.overwrite_model_widget.value
            self._value.epochs = self.epochs_widget.value
            self._value.lr = self.lr_widget.value
            self._value.evaluate_calibration = self.evaluate_calibration_widget.value
            self._value.evaluation_mode = self.evaluation_mode_widget.selected_app.value
            self._value.reliability_mode = (
                self.reliability_mode_widget.selected_app.value
            )
            self._value.plot_reliability_curves = (
                self.plot_reliability_curves_widget.value
            )
            self._value.plot_temp_changes = self.plot_temp_changes_widget.value
            self._value.plot_probability_distributions = (
                self.plot_probability_distributions_widget.value
            )
        else:
            self._value = self.value_original
            self._value.run_calibration = False

        return self._value

    @value.setter
    def value(self, v):
        self._value = v
