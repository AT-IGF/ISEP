from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)


from src.common.config import Config
from src.common.config.configs import PredictionsMapperConfig

from src.ui.common import (
    LabelValueWidget,
    DirectorySelectorWidget,
)
from src.ui.dataViewer import aggregatedSamples as aggregated


class ThresholdWidget(QWidget):
    def __init__(self, signals):
        super().__init__()
        self.current_config = Config.get(PredictionsMapperConfig)
        config = Config.get(PredictionsMapperConfig)
        self._value = config.thresholds
        self._value_original = config.thresholds

        self.common_threshold_widget = LabelValueWidget(
            "Threshold:",
            self._value.threshold,
            signals,
            val_type=float,
            tooltip="Threshold at which summary will be run.",
            margins=(10, 5, 0, 0),
            bottom=0,
            top=1,
        )

        self.per_type_thresholds_path_widget = DirectorySelectorWidget(
            "Class threshold path",
            self._value.per_type_thresholds_path,
            value_changed=signals.value_changed,
            show_modal=signals.show_modal,
            selector="FILE",
            extensions=DirectorySelectorWidget.JSON_FILE_EXTENSION,
            tooltip='Mapping file in json format containing information what threshold should be set for what pollen type (class).\
                <br/><b>NOTE</b>: file should be create by the user, example output would be f1 scores from the model builder -> supervised -> run summaries -> F1-score curve\
                <br/><b>Example input</b>: { "Alnus": 0.4, "Corlus": 0.2 }',
            margins=(10, 5, 0, 0),
        )

        sub_apps = [
            aggregated.Radio(
                self._value.COMMON_THRESHOLD,
                self._value.threshold_type,
                widget=self.common_threshold_widget,
                label="Single threshold for all types",
            ),
            aggregated.Radio(
                self._value.CLASS_THRESHOLD,
                self._value.threshold_type,
                widget=self.per_type_thresholds_path_widget,
                label="Per type thresholds",
            ),
        ]

        self.plot_style_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps,
            signals.value_changed,
            label="Threshold mode:",
            layout="Horizontal",
            margins=(0, 10, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Below",
            tooltip="The way in which plot is presented.",
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.plot_style_widget)
        layoutV.setContentsMargins(10, 0, 0, 0)
        layoutV.setSpacing(0)
        self.setLayout(layoutV)

    @property
    def value(self):
        if (
            self.plot_style_widget.selected_app.value
            == self._value_original.COMMON_THRESHOLD
        ):
            self._value = self._value_original
            self._value.threshold_type = self._value_original.COMMON_THRESHOLD
            self._value.threshold = self.common_threshold_widget.value
        else:
            self._value = self._value_original
            self._value.threshold_type = self._value_original.CLASS_THRESHOLD
            self._value.per_type_thresholds_path = (
                self.per_type_thresholds_path_widget.value
            )
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
