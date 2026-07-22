from functools import partial
import logging
from src.ui.common.General import set_style_sheet
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QRadioButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)

from src.ui.common.FieldsHelper import toogle_field_visibility
from src.ui.common import IconLabel
from src.ui.common.Helpers.TooltipHelper import add_tooltip_or_text_to_layout
from src.ui.common import LabelValueWidget


class Radio:
    def __init__(self, value, selected_value, widget=None, label=None):
        self.value = value
        self.button = QRadioButton(label if label != None else value)
        self.is_selected_original = selected_value == value
        self.button.setChecked(self.is_selected_original)
        self.is_selected = self.is_selected_original
        self.widget = widget

    def set_value(self, value):
        self.value = value


class OtherRadio(Radio):
    def __init__(self, values, selected_value, signals, tooltip=None):
        self._values = values
        self._init_value = self.get_other_value(selected_value)

        other_widget = LabelValueWidget(
            label="",
            value=self._init_value,
            singals=signals,
            val_type=str,
            tooltip=tooltip,
            width=100,
        )

        super().__init__(
            value=self._init_value,
            selected_value=selected_value,
            widget=other_widget,
            label="Other",
        )

        other_widget.editingFinished.connect(
            lambda val: self.on_other_editing_finished(val)
        )

    def on_other_editing_finished(self, val):
        new_val = self.get_other_value(val)
        self.set_value(new_val)

    def get_other_value(self, value):
        if value == None or value in self._values:
            return ""
        return value


class RadioSelectorWidget(QWidget):
    def show(self):
        if self.force_hide:
            logging.getLogger("ui").debug(
                f"Force hide enabled, component will not show {self}"
            )
            return
        return super().show()

    def __init__(
        self,
        parent,
        sub_apps,
        value_changed,
        label=None,
        layout="Vertical",
        sub_widgets_layout="Below",
        tooltip=None,
        margins=None,
        is_white_background=False,
        force_hide=False,
    ):
        super(RadioSelectorWidget, self).__init__(parent)

        self.force_hide = force_hide
        if self.force_hide:
            self.deleteLater()

        if layout == "Horizontal":
            main_layout = QHBoxLayout()
        else:
            main_layout = QVBoxLayout()

        label_widget = None
        if label != None:
            label_widget = QLabel(label)
            main_layout.addWidget(label_widget)

        add_tooltip_or_text_to_layout(
            tooltip=tooltip, label_widget=label_widget, layout=main_layout, spacer=True
        )

        self.sub_apps = sub_apps
        self.value_changed = value_changed

        for sub_app in self.sub_apps:
            main_layout.addWidget(sub_app.button)
            sub_app.button.clicked.connect(
                partial(self.on_app_button_click, self.sub_apps, sub_app)
            )  # https://stackoverflow.com/questions/67057972/pyqt5-clicked-button-created-in-loop

        if sub_widgets_layout == "Inline":
            for sub_app in self.sub_apps:
                main_layout.addWidget(sub_app.widget)
            self.setup_layout(main_layout, margins)
            self.setLayout(main_layout)
        else:
            layout_subwidgets = QVBoxLayout()
            layout_subwidgets.addLayout(main_layout)
            for sub_app in self.sub_apps:
                layout_subwidgets.addWidget(sub_app.widget)

            self.setup_layout(main_layout, margins)
            self.setup_layout(layout_subwidgets, margins)
            self.setLayout(layout_subwidgets)

        self.selected_app = None
        self.selected_app_original = None
        for sub_app in sub_apps:
            if sub_app.is_selected:
                self.selected_app = sub_app
                self.selected_app_original = sub_app
                self.on_app_button_click(self.sub_apps, sub_app)

        if is_white_background:
            self.setAutoFillBackground(True)
            p = self.palette()
            p.setColor(self.backgroundRole(), Qt.white)
            self.setPalette(p)

    def setup_layout(self, layout, margins=None):
        layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        if margins != None:
            layout.setContentsMargins(*margins)  # left, top, right, bottom

        layout.setAlignment(Qt.AlignLeft)
        layout.setSpacing(0)
        layout.addStretch(1)

    def on_app_button_click(self, sub_apps: list[Radio], sub_app: Radio):
        for _sub_app in sub_apps:
            show_child = False
            if _sub_app is sub_app:
                show_child = True
                _sub_app.button.setStyleSheet("font-weight: bold")
                _sub_app.is_selected = True
                self.selected_app = _sub_app
            else:
                show_child = False
                _sub_app.button.setStyleSheet("font-weight: normal")
                _sub_app.is_selected = False

            if _sub_app.widget != None:
                toogle_field_visibility(_sub_app.widget, show=show_child)

        if self.selected_app_original == sub_app:
            self.value_changed.emit(self, False)
        else:
            self.value_changed.emit(self, True)

    def update(self, value):
        selected_app = None
        for sub_app in self.sub_apps:
            if value == sub_app.value:
                selected_app = sub_app
                break
        if selected_app == None:
            logging.getLogger("ui").warning(
                f"Something went wrong during radio button update, value='{value}'"
            )
            return

        sub_app.button.setChecked(True)
        self.selected_app = sub_app
        self.on_app_button_click(self.sub_apps, selected_app)

    def selected_app_value(self):
        if self.selected_app.value == "None":
            return None
        return self.selected_app.value
