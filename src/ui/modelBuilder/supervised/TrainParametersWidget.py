from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit

from src.common import Consts
from src.common.config.configs.models.modelBuilder import TrainParametersModel
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common import (
    LabelValueWidget,
    MeasurementWidget,
    SectionWidget,
)
from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.common.types import Messages as messages
from src.ui.common.buttons.ResetToFactoryDefaultsWidget import (
    ResetToFactoryDefaultsWidget,
)
from src.ui.common import IconLabel
from PyQt5.QtGui import QColor

from src.ui.modelBuilder.common import EarlyStoppingWidget, LearningRateReducerWidget


class TrainParametersWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    filter_value_changed = pyqtSignal(object, bool)
    test_filter_value_changed = pyqtSignal(object, bool)
    modify_defaults_value_changed = pyqtSignal(object, bool)

    def __init__(self, config: TrainParametersModel, signals: SettingsSignals):
        super().__init__()
        self.config = config
        self._value = config
        self.value_original = config

        layoutV_plots = QVBoxLayout()
        self.setLayout(layoutV_plots)

        self.general_section_widget = SectionWidget("General")
        self.single_type_count_widget = LabelValueWidget(
            "Single type count",
            (
                0
                if self.config.single_type_count == None
                else self.config.single_type_count
            ),
            signals,
            val_type=int,
            tooltip="",
            margins=(10, 10, 0, 0),
            bottom=0,
        )
        sampling_stratrgy = self.config.sampling_strategy
        sub_apps = [
            aggregated.Radio(None, sampling_stratrgy, label="Unset"),
            aggregated.Radio(
                TrainParametersModel.OVERSAMPLE_STRATEGY,
                sampling_stratrgy,
                widget=IconLabel(
                    "mdi.alert-outline",
                    text="Warning: Oversample strategy takes effect on cache dataset creation",
                    color=QColor(185, 144, 8, 255),
                    size=24,
                ),
                label="Oversample",
            ),
            aggregated.Radio(
                TrainParametersModel.ALING_WEIGHTS_STRATEGY,
                sampling_stratrgy,
                label="Align weights",
            ),
        ]
        self.sampling_strategy_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=self.value_changed,
            label="Sampling strategy:",
            tooltip="Class imbalance strategy.\nNote: Oversample requires generation of a new set",
            layout="Horizontal",
            margins=(5, 5, 0, 0),
        )

        self.custom_buffer_size_widget = LabelValueWidget(
            "",
            (
                0
                if self.config.custom_buffer_size == None
                else self.config.custom_buffer_size
            ),
            signals,
            val_type=int,
            margins=(0, 0, 0, 0),
            bottom=0,
            width=100,
        )
        buffer_size_mode = self.config.buffer_size_mode
        default_buffer_size = QLineEdit(str(Consts.BUFFER_SIZE_DEFAULT))
        default_buffer_size.setStyleSheet(
            """
            QLineEdit[readOnly="true"] {
                background: #f0f0f0;
                color: #606060;
            }
        """
        )
        default_buffer_size.setProperty("readOnly", True)
        sub_apps = [
            aggregated.Radio(
                None,
                buffer_size_mode,
                label="Default",
                widget=default_buffer_size,
            ),
            aggregated.Radio(
                TrainParametersModel.ALL_SAMPLES_BUFFER_MODE,
                buffer_size_mode,
                label="All samples",
            ),
            aggregated.Radio(
                TrainParametersModel.CUSTOM_BUFFER_MODE,
                buffer_size_mode,
                label="Custom size",
                widget=self.custom_buffer_size_widget,
            ),
        ]
        self.buffer_size_mode_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=self.value_changed,
            label="Buffer size mode:",
            tooltip="How many samples is trained at once. To high samples count can cause out of memory exception, however it allows to achieve best accuracies. Lower buffer sizes saves memory by loading only data chunks for training.",
            layout="Horizontal",
            margins=(10, 5, 0, 0),
            sub_widgets_layout="Inline",
        )
        self.smoothing_widget = LabelValueWidget(
            "Smoothing",
            0 if self.config.smoothing == None else self.config.smoothing,
            signals,
            val_type=float,
            tooltip="Amount of probability assigned to other labels. Prevents model from being overconfident.\n\
                                                     E.g. having three classes 'A', 'B' and 'C', if type is labeled as 'A' setting smotting at 0.1 will assign 0.05 probabilities to 'B' and 'C' and 0.9 to 'A'.",
            margins=(10, 10, 0, 0),
            bottom=0,
            top=1,
            decimals=2,
        )
        self.epochs_widget = LabelValueWidget(
            "Epochs",
            0 if self.config.epochs == None else self.config.epochs,
            signals,
            val_type=int,
            tooltip=messages.EPOCHS_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )
        self.lr_widget = LabelValueWidget(
            "Learning rate",
            0 if self.config.lr == None else self.config.lr,
            signals,
            val_type=float,
            tooltip=messages.LR_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )
        self.weight_decay_widget = LabelValueWidget(
            "Weight decay",
            0 if self.config.weight_decay == None else self.config.weight_decay,
            signals,
            val_type=float,
            tooltip=messages.WEIGHT_DECAY_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )

        self.early_stopping_widget = EarlyStoppingWidget(
            config=self.config.early_stopping, signals=signals
        )

        self.lr_reducer_widget = LearningRateReducerWidget(
            config=self.config.lr_reducer, signals=signals
        )

        self.roll_back_widget = SectionWidget("Roll back")
        self.reset_to_factory_defaults_widget = ResetToFactoryDefaultsWidget(
            self.reset_to_factory_defaults
        )

        modify_defaults = False
        self.modify_training_defaults_widget = MeasurementWidget(
            modify_defaults,
            label="Modify training default parameters",
            tooltip=messages.DEFAULT_TRAIN_PARAMS_TEXT,
            value_changed=self.modify_defaults_value_changed,
            children=[
                self.general_section_widget,
                self.epochs_widget,
                self.single_type_count_widget,
                self.sampling_strategy_widget,
                self.buffer_size_mode_widget,
                self.lr_widget,
                self.smoothing_widget,
                self.weight_decay_widget,
                self.early_stopping_widget,
                self.lr_reducer_widget,
                self.roll_back_widget,
                self.reset_to_factory_defaults_widget,
            ],
            layout="Vertical",
            spacing_children=10,
            margins=(0, 0, 0, 0),
        )

        self.value_changed.connect(
            lambda obj, changed: signals.value_changed.emit(obj, changed)
        )
        layoutV_plots.setSpacing(0)
        layoutV_plots.addWidget(self.modify_training_defaults_widget)
        self.setLayout(layoutV_plots)

    @property
    def value(self):
        if self.modify_training_defaults_widget.value == True:
            self._value.run_training = True
            self._value.single_type_count = self.single_type_count_widget.value
            self._value.sampling_strategy = (
                self.sampling_strategy_widget.selected_app.value
            )
            self._value.buffer_size_mode = (
                self.buffer_size_mode_widget.selected_app.value
            )
            self._value.custom_buffer_size = self.custom_buffer_size_widget.value
            self._value.smoothing = self.smoothing_widget.value
            self._value.epochs = self.epochs_widget.value
            self._value.lr = self.lr_widget.value
            self._value.weight_decay = self.weight_decay_widget.value
            self._value.early_stopping = self.early_stopping_widget.value
            self._value.lr_reducer = self.lr_reducer_widget.value
        else:
            self._value.run_training = False
            self._value = self.value_original

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def reset_to_factory_defaults(self):
        model = TrainParametersModel()

        self.single_type_count_widget.update(model.single_type_count)
        self.sampling_strategy_widget.update(model.sampling_strategy)
        self.buffer_size_mode_widget.update(model.buffer_size_mode)
        self.custom_buffer_size_widget.update(model.custom_buffer_size)
        self.smoothing_widget.update(model.smoothing)
        self.epochs_widget.update(model.epochs)
        self.lr_widget.update(model.lr)
        self.weight_decay_widget.update(model.weight_decay)
        self.early_stopping_widget.update(model.early_stopping)
        self.lr_reducer_widget.update(model.lr_reducer)
