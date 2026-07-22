from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtGui import QIntValidator

from varname import nameof

import numpy as np

from src.ui.common.FieldsHelper import emit_on_change, on_number_field_edit_finish
from src.ui.common.NullableIntValidator import type_validatior
from src.ui.common import IconLabel
from src.ui.common.Helpers.TooltipHelper import add_tooltip_or_text_to_layout
from functools import partial


class LabelValueWidget(QWidget):
    editingFinished = pyqtSignal(str)

    def __init__(
        self,
        label,
        value,
        singals,
        val_type=None,
        suffix_label=None,
        tooltip=None,
        width=250,
        min_width=250,
        read_only=False,
        margins=None,
        nullable=True,
        prefix_label=None,
        **kwargs,
    ):
        super().__init__()
        layoutH_combine_files = QHBoxLayout()
        if label != None:
            value_label = QLabel(label)
            layoutH_combine_files.addWidget(value_label)

        self.value_changed = singals.value_changed
        self.show_modal = singals.show_modal
        self.val_type = val_type

        add_tooltip_or_text_to_layout(
            tooltip=tooltip,
            label_widget=value_label,
            layout=layoutH_combine_files,
            spacer=True,
        )

        self._value = self.get_value_or_empty(value)
        self._value_original = value
        self._value_field = QLineEdit(str(self.get_value_or_empty(value)))
        if read_only == True:
            self._value_field.setStyleSheet(
                """
                QLineEdit[readOnly="true"] {
                    background: #f0f0f0;
                    color: #606060;
                }
            """
            )
            self._value_field.setProperty("readOnly", True)

        if min_width != None:
            self._value_field.setMinimumWidth(min_width)
        if width != None:
            self._value_field.setFixedWidth(width)

        if prefix_label != None:
            prefix_label_widget = QLabel(prefix_label)
            prefix_label_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            prefix_label_widget.setStyleSheet(
                "QLabel { background: transparent; padding-left: 2px; }"
            )
            layoutH_combine_files.addWidget(prefix_label_widget)

        layoutH_combine_files.addWidget(self._value_field)

        if suffix_label != None:
            suffix_label_widget = QLabel(suffix_label)
            suffix_label_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            suffix_label_widget.setStyleSheet(
                "QLabel { background: transparent; padding-left: 2px; }"
            )
            layoutH_combine_files.addWidget(suffix_label_widget)

        layoutH_combine_files.setContentsMargins(
            0, 10, 0, 0
        )  # left, top, right, bottom
        if margins != None:
            layoutH_combine_files.setContentsMargins(
                *margins
            )  # left, top, right, bottom
        layoutH_combine_files.addStretch(1)
        layoutH_combine_files.setSpacing(0)

        self.setLayout(layoutH_combine_files)
        validator = type_validatior(
            self, int if val_type is None else val_type, **kwargs
        )

        self._value_field.editingFinished.connect(
            lambda: on_number_field_edit_finish(
                self,
                nameof(self.value),
                self._value_field,
                validator=validator,
                show_modal=singals.show_modal,
                val_type=val_type,
                nullable=nullable,
            )
        )

        self._value_field.editingFinished.connect(
            lambda: self.editingFinished.emit(self._value_field.text())
        )
        emit_on_change(self._value_field, value, self.value_changed)

    def get_value_or_empty(self, value):
        return value if value != None else ""

    @property
    def value(self):
        if self._value == "":
            return None
        if self._value != "" and self._value != None and self.val_type == float | None:
            converted_value = float(self._value)
        elif self._value != "" and self._value != None and self.val_type == int | None:
            converted_value = int(self._value)
        elif self.val_type != None:
            converted_value = self.val_type(self._value)
        elif self._value_original != None:
            converted_value = type(self._value_original)(self._value)
        else:
            converted_value = str(self._value)
        return converted_value

    @value.setter
    def value(self, value):
        if value == None:
            value = ""

        if self._value != value:
            self._value = value

    def text(self):
        return self.value

    def setText(self, value):
        self._value_field.setText(value)

    def update(self, value):
        self.setText(str(value))
        self._value_field.editingFinished.emit()
