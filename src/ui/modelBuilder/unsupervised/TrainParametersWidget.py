from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from src.common.config.configs.models.modelBuilderUnsupervised import (
    TrainParametersModel,
)
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common import (
    LabelValueWidget,
    MeasurementWidget,
    SectionWidget,
)
from src.ui.common.types import Messages as messages
from src.ui.modelBuilder.common import EarlyStoppingWidget, LearningRateReducerWidget
from src.ui.common.buttons import ResetToFactoryDefaultsWidget


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
                self.lr_widget,
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
            self._value.epochs = self.epochs_widget.value
            self._value.lr = self.lr_widget.value
            self._value.weight_decay = self.weight_decay_widget.value
            self._value.early_stopping = self.early_stopping_widget.value
            self._value.lr_reducer = self.lr_reducer_widget.value
        else:
            self._value = self.value_original

        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def reset_to_factory_defaults(self):
        model = TrainParametersModel()

        self.epochs_widget.update(model.epochs)
        self.lr_widget.update(model.lr)
        self.weight_decay_widget.update(model.weight_decay)
        self.early_stopping_widget.update(model.early_stopping)
        self.lr_reducer_widget.update(model.lr_reducer)
