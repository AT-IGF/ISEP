from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
import numpy as np

from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.common.FieldsHelper import emit_on_change, on_number_field_edit_finish
from varname import nameof
from PyQt5.QtGui import QIntValidator
from src.ui.common import IconLabel


class SameTypeCountWidget(QWidget):
    def __init__(self, config, singals: SettingsSignals):
        super().__init__()
        self.config = config
        self.same_type_count = self.config.same_type_count

        layoutH_same_type_count = QHBoxLayout()
        same_type_count_label = QLabel("Same type count")
        same_type_count_help = IconLabel(
            "mdi.help-circle-outline",
            tooltip="Count of samples from the same type to be displayed.",
            color="darkBlue",
        )
        colon_label = QLabel(":")
        same_type_count_field = QLineEdit(str(self.config.same_type_count))
        same_type_count_field.editingFinished.connect(
            lambda: on_number_field_edit_finish(
                self,
                prop=nameof(self.same_type_count),
                field=same_type_count_field,
                validator=QIntValidator(0, np.iinfo(np.int32).max),
                show_modal=singals.show_modal,
            )
        )

        emit_on_change(
            same_type_count_field, self.same_type_count, singals.value_changed
        )
        layoutH_same_type_count.addWidget(same_type_count_label)
        layoutH_same_type_count.addWidget(same_type_count_help)
        layoutH_same_type_count.addWidget(colon_label)
        layoutH_same_type_count.addWidget(same_type_count_field)
        layoutH_same_type_count.addStretch(1)
        self.setLayout(layoutH_same_type_count)
