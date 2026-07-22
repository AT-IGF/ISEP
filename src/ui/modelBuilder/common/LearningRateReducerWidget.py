from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from src.common.config.configs.models.common import LearningRateReducerModel
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common import SectionWidget, LabelValueWidget, MeasurementWidget
from src.ui.common.types import Messages as messages


class LearningRateReducerWidget(QWidget):
    value_changed = pyqtSignal(object, bool, object)
    paths_changed = pyqtSignal(object, bool, object)

    def __init__(
        self,
        config: LearningRateReducerModel,
        signals: SettingsSignals,
    ):
        super().__init__()
        self._value: LearningRateReducerModel = config
        self.value_original: LearningRateReducerModel = config

        self.lrr_section_widget = SectionWidget("Learning rate reducer")
        self.patience_widget = LabelValueWidget(
            "Patience",
            0 if config.patience == None else config.patience,
            signals,
            val_type=int,
            tooltip=messages.REDUCER_PATIENCE_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )
        self.min_lr_widget = LabelValueWidget(
            "Min learning rate",
            0 if config.min_lr == None else config.min_lr,
            signals,
            val_type=float,
            tooltip=messages.MIN_LR_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )
        self.min_delta_widget = LabelValueWidget(
            "Min delta",
            0 if config.min_delta == None else config.min_delta,
            signals,
            val_type=float,
            tooltip=messages.MIN_DELTA_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )
        self.factor_widget = LabelValueWidget(
            "Decrease factor",
            0 if config.factor == None else config.factor,
            signals,
            val_type=float,
            tooltip=messages.DECREASE_FACTOR_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )

        self.enabled_widget = MeasurementWidget(
            config.enabled,
            label="Is early stopping enabled",
            tooltip="Allows to stop model training earlier based on conditions",
            value_changed=signals.value_changed,
            children=[
                self.patience_widget,
                self.min_lr_widget,
                self.min_delta_widget,
                self.factor_widget,
            ],
            layout="Vertical",
            margins=(10, 10, 0, 0),
        )

        layoutH = QVBoxLayout()
        layoutH.setAlignment(Qt.AlignLeft)
        layoutH.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        layoutH.setSpacing(0)
        layoutH.addWidget(self.lrr_section_widget)
        layoutH.addWidget(self.enabled_widget)
        layoutH.addStretch(1)
        self.setLayout(layoutH)

    @property
    def value(self):
        self._value.patience = self.patience_widget.value
        self._value.min_lr = self.min_lr_widget.value
        self._value.min_delta = self.min_delta_widget.value
        self._value.factor = self.factor_widget.value
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def update(self, value: LearningRateReducerModel):
        self.patience_widget.update(value.patience)
        self.min_lr_widget.update(value.min_lr)
        self.min_delta_widget.update(value.min_delta)
        self.factor_widget.update(value.factor)
