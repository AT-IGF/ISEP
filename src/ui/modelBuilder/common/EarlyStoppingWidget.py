from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel

from src.common.config.configs.models.common import EarlyStoppingModel
from src.common.tensorflow.InputModelNames import TRAIN_MODELS
from src.common.config import Config, ModelBuilderConfig, PathsConfig
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common.FieldsHelper import emit_on_change, on_number_field_edit_finish
from varname import nameof
from PyQt5.QtGui import QDoubleValidator
from src.ui.common import IconLabel
from src.ui.dataViewer import Signal
from src.ui.common import MultiCheckboxWidget
from src.ui.common import SectionWidget, LabelValueWidget, MeasurementWidget
from src.ui.common.types import Messages as messages


class EarlyStoppingWidget(QWidget):
    value_changed = pyqtSignal(object, bool, object)
    paths_changed = pyqtSignal(object, bool, object)

    def __init__(
        self,
        config: EarlyStoppingModel,
        signals: SettingsSignals,
    ):
        super().__init__()
        self._value: EarlyStoppingModel = config
        self.value_original: EarlyStoppingModel = config

        self.early_stopping_widget = SectionWidget("Early stopping")
        self.patience_widget = LabelValueWidget(
            "Patience",
            0 if config.patience == None else config.patience,
            signals,
            val_type=int,
            tooltip=messages.EARLY_STOPPING_PATIENCE_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )

        self.min_delta_widget = LabelValueWidget(
            "Min delta",
            0 if config.min_delta == None else config.min_delta,
            signals,
            val_type=float,
            tooltip=messages.EARLY_STOPPING_MIN_DELTA_TRAIN_PARAMS_TEXT,
            margins=(10, 10, 0, 0),
            bottom=0,
        )

        self.enabled_widget = MeasurementWidget(
            config.enabled,
            label="Is early stopping enabled",
            tooltip="Allows to stop model training earlier based on conditions",
            value_changed=signals.value_changed,
            children=[self.patience_widget, self.min_delta_widget],
            layout="Vertical",
            margins=(10, 10, 0, 0),
        )

        layoutH = QVBoxLayout()
        layoutH.setAlignment(Qt.AlignLeft)
        layoutH.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        layoutH.setSpacing(0)
        layoutH.addWidget(self.early_stopping_widget)
        layoutH.addWidget(self.enabled_widget)
        layoutH.addStretch(1)
        self.setLayout(layoutH)

    @property
    def value(self):
        self._value.patience = self.patience_widget.value
        self._value.min_delta = self.min_delta_widget.value
        self._value.enabled = self.enabled_widget.value
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def update(self, value: EarlyStoppingModel):
        self.patience_widget.update(value.patience)
        self.min_delta_widget.update(value.min_delta)
        self.enabled_widget.update(value.enabled)
