from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
)

from varname import nameof

from src.ui.common import IconLabel

from src.ui.common.FieldsHelper import (
    map_check_state,
    map_check_state_to_bool,
    toogle_fields_visibility,
)
from src.ui.common.Helpers.TooltipHelper import add_tooltip_or_text_to_layout


class MeasurementWidget(QWidget):
    visibility_signal = pyqtSignal(bool)

    def __init__(
        self,
        value,
        label,
        tooltip: str = None,
        value_changed=None,
        children: list = [],
        callbacks: dict = {},
        layout="Horizontal",
        margins=None,
        spacing_children=None,
        emit_on_change=True,
        change_signal=None,
        suffix_text="",
        margins_children=None,
    ):
        super().__init__()
        self._original_value = value
        self.value = value
        self.value_changed = value_changed
        layoutV_children = QVBoxLayout()
        [layoutV_children.addWidget(child) for child in children]
        layoutV_children.setSpacing(0)
        if spacing_children != None:
            layoutV_children.setSpacing(spacing_children)
        if margins_children != None:
            layoutV_children.setContentsMargins(
                *margins_children
            )  # left, top, right, bottom

        if layout == "Vertical":
            layout = QVBoxLayout()
        else:
            layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)

        parent_layout = QHBoxLayout()
        parent_layout.setAlignment(Qt.AlignLeft)

        self.checkbox = QCheckBox()
        self.plot_spectrum_label = QLabel(label)
        self.checkbox.setCheckState(map_check_state(bool(value)))
        if change_signal != None:
            change_signal.connect(
                lambda _value: self.checkbox.setCheckState(
                    map_check_state(bool(_value))
                )
            )
        toogle_fields_visibility(
            children,
            map_check_state_to_bool(self.checkbox.checkState()),
            callbacks,
        )
        self.checkbox.clicked.connect(lambda x: self.visibility_signal.emit(x))
        self.checkbox.clicked.connect(
            lambda x: toogle_fields_visibility(children, x, callbacks)
        )
        self.checkbox.clicked.connect(lambda x: self.on_value_change(x))
        if emit_on_change == True:
            self.checkbox.clicked.connect(
                lambda x: value_changed.emit(self, x != bool(self._original_value))
            )

        parent_layout.addWidget(self.checkbox)
        spacer_widget = QSpacerItem(5, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        parent_layout.addItem(spacer_widget)
        parent_layout.addWidget(self.plot_spectrum_label)
        add_tooltip_or_text_to_layout(
            tooltip=tooltip,
            label_widget=self.plot_spectrum_label,
            layout=parent_layout,
            spacer=True,
            suffix_text=suffix_text,
        )
        parent_layout.setSpacing(0)

        layout.addLayout(parent_layout)
        layout.addLayout(layoutV_children)

        layout.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom
        if margins != None:
            layout.setContentsMargins(*margins)  # left, top, right, bottom
        layout.addStretch(1)
        self.setLayout(layout)

    def is_checked(self):
        return self.checkbox.isChecked()

    def on_value_change(self, value):
        self.value = bool(value)
        if self.value_changed is None:
            return
        if self._original_value != value:
            self.value_changed.emit(self.checkbox, True)
        else:
            self.value_changed.emit(self.checkbox, False)

    def update(self, value):
        self.checkbox.setCheckState(map_check_state(bool(value)))
        self.checkbox.clicked.emit(bool(value))
