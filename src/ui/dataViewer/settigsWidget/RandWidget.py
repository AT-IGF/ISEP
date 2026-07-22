from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel

from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common.FieldsHelper import emit_on_change, on_number_field_edit_finish
from varname import nameof
from PyQt5.QtGui import QDoubleValidator
from src.ui.common import IconLabel


class RandWidget(QWidget):
    def __init__(self, config, singals: SettingsSignals):
        super().__init__()
        self.config = config
        self.rand_0_1_frequency = self.config.rand_0_1_frequency

        layoutH_rand_0_1_frequency = QHBoxLayout()
        rand_0_1_frequency_label = QLabel("Random frequency")
        rand_0_1_frequency_help = IconLabel(
            "mdi.help-circle-outline",
            tooltip="Randomizes particle type that will be processed. If '0' every particle will be taken. If '0.5' every second",
            color="darkBlue",
        )
        colon_label = QLabel(":")
        rand_0_1_frequency_field = QLineEdit(str(self.config.rand_0_1_frequency))
        rand_0_1_frequency_field.editingFinished.connect(
            lambda: on_number_field_edit_finish(
                self,
                prop=nameof(self.rand_0_1_frequency),
                field=rand_0_1_frequency_field,
                validator=QDoubleValidator(0, 1, 50),
                show_modal=singals.show_modal,
            )
        )
        emit_on_change(
            rand_0_1_frequency_field,
            self.config.rand_0_1_frequency,
            singals.value_changed,
        )

        layoutH_rand_0_1_frequency.addWidget(rand_0_1_frequency_label)
        layoutH_rand_0_1_frequency.addWidget(rand_0_1_frequency_help)
        layoutH_rand_0_1_frequency.addWidget(colon_label)
        layoutH_rand_0_1_frequency.addWidget(rand_0_1_frequency_field)
        layoutH_rand_0_1_frequency.setSpacing(0)
        layoutH_rand_0_1_frequency.addStretch(1)
        self.setLayout(layoutH_rand_0_1_frequency)
