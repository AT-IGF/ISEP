from PyQt5.QtWidgets import QWidget, QVBoxLayout

from src.common import Consts
from src.ui.common import LabelValueWidget
from src.ui.dataViewer.aggregatedSamples.AggregatorWidget import (
    Radio,
    RadioSelectorWidget,
)


class PcaComponentsWidget(QWidget):
    def __init__(self, pca_components, singals, margins=None, is_list=None):
        super().__init__()

        if is_list is None:
            is_list = isinstance(pca_components, list)
        _pca_components_int = []
        _pca_components_float = []
        int_default = [1] if is_list else 1
        float_default = [0.95] if is_list else 0.95
        if pca_components == None:
            selected_value = None
            _pca_components_int = int_default
            _pca_components_float = float_default
        elif (
            is_list
            and pca_components[0] > 0
            and pca_components[0] < 1
            or not is_list
            and pca_components > 0
            and pca_components < 1
        ):
            _pca_components_float = pca_components
            _pca_components_int = int_default
            selected_value = "perc"
        else:
            _pca_components_float = float_default
            _pca_components_int = pca_components
            selected_value = "count"

        self.percetile_widget = LabelValueWidget(
            "",
            _pca_components_float,
            singals,
            val_type=list[float] if is_list else float,
            suffix_label=None,
            tooltip=None,
            width=100,
            bottom=0.01,
            top=1,
            margins=(0, 0, 0, 0),
        )

        self.count_widget = LabelValueWidget(
            "",
            _pca_components_int,
            singals,
            val_type=list[int] if is_list else int,
            suffix_label=None,
            tooltip=None,
            width=100,
            bottom=1,
            top=Consts.INT_MAX,
            margins=(0, 0, 0, 0),
        )

        sub_apps = [
            Radio(None, selected_value, label="None"),
            Radio(
                "perc",
                selected_value,
                widget=self.percetile_widget,
                label="Percentile",
            ),
            Radio(
                "count",
                selected_value,
                widget=self.count_widget,
                label="Components count",
            ),
        ]
        self.pca_components_widget = RadioSelectorWidget(
            self,
            sub_apps=sub_apps,
            value_changed=singals.value_changed,
            label="Pca components:",
            layout="Horizontal",
            sub_widgets_layout="Inline",
            tooltip="Number of dimensions to which data should be reduced.<br/><b>Note</b>: above 50 dimensions hdbscan slows down drastically due to switch to different way of distance calculations.",
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.pca_components_widget)
        layoutV.addStretch()
        layoutV.setContentsMargins(0, 10, 0, 0)  # left, top, right, bottom
        if margins != None:
            layoutV.setContentsMargins(*margins)  # left, top, right, bottom

        self.setLayout(layoutV)

    @property
    def value(self):
        if self.pca_components_widget.selected_app.value == "perc":
            return self.percetile_widget.value
        elif self.pca_components_widget.selected_app.value == "count":
            return self.count_widget.value
        else:
            return None

    @value.setter
    def value(self, value):
        self._value = value
