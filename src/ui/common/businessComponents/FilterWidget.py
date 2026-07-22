from PyQt5.QtWidgets import QWidget, QVBoxLayout

from src.core.path import PathHelper
from src.ui.common import DirectorySelectorWidget, MeasurementWidget
from src.common import Consts


class FilterWidget(QWidget):
    def __init__(self, filter_path, singals, margins=None):
        super().__init__()
        self._value = filter_path
        self._value_original = filter_path

        python_files_selector = "Python files (*.py)"
        self.filter_rel_path_widget = DirectorySelectorWidget(
            "",
            self._value,
            value_changed=singals.value_changed,
            show_modal=singals.show_modal,
            selector="FILE",
            extensions=python_files_selector,
            margins=(0, 0, 0, 0),
            default_path=PathHelper.get_absolute_path(
                Consts.RESOURCES_PATH, "common/filters", raise_on_not_found=False
            ),
        )
        self.filter_widget = MeasurementWidget(
            self._value != None,
            label="Filter path",
            tooltip="Path to the file that will be used for samples filtration.\
                <br/><b>Default path with samples</b>: resources/common/filters\
                <br/><b>Note</b>: for best match same filter should be used for both the scaler and trained model.",
            value_changed=singals.value_changed,
            children=[self.filter_rel_path_widget],
            layout="Horizontal",
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.filter_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        if margins != None:
            layoutV.setContentsMargins(*margins)  # left, top, right, bottom

        self.setLayout(layoutV)

    @property
    def value(self):
        if not self.filter_widget.is_checked():
            return None
        return self.filter_rel_path_widget.value

    @value.setter
    def value(self, value):
        self._value = value
