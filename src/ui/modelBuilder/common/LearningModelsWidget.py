from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel

from src.common.tensorflow.InputModelNames import TRAIN_MODELS
from src.common.config import Config, ModelBuilderConfig, PathsConfig
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common.FieldsHelper import emit_on_change, on_number_field_edit_finish
from varname import nameof
from PyQt5.QtGui import QDoubleValidator
from src.ui.common import IconLabel
from src.ui.dataViewer import Signal
from src.ui.common import MultiCheckboxWidget


class LearningModelsWidget(QWidget):
    value_changed = pyqtSignal(object, bool, object)
    paths_changed = pyqtSignal(object, bool, object)

    def __init__(self, learningModels, singals: SettingsSignals):
        super().__init__()
        self._value = learningModels[:]
        self.value_original = learningModels[:]
        self.value_changed = singals.value_changed

        values = []
        for val in TRAIN_MODELS:
            values.append({val.split("_")[0]: val})

        self.learning_models_widget = MultiCheckboxWidget(
            options=values, singals=singals, preselected=self._value
        )

        tooltip_widget = IconLabel(
            "mdi.help-circle-outline",
            tooltip="Model inputs used for training and further for prediction purposes. Size modality is calculated based on the scattering, no additional input is needed.",
            color="darkBlue",
            text=":",
        )

        layoutH = QHBoxLayout()
        layoutH.setAlignment(Qt.AlignLeft)
        layoutH.setContentsMargins(10, 0, 0, 0)  # left, top, right, bottom
        layoutH.setSpacing(0)
        layoutH.addWidget(QLabel("Input modalities"))
        layoutH.addWidget(tooltip_widget)
        layoutH.addWidget(self.learning_models_widget)
        layoutH.addStretch(1)
        self.setLayout(layoutH)

    def get_selected_values(self):
        return self.learning_models_widget.values
