from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLayout


from src.common.config.configs.models.modelBuilder import SummaryModel
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig

from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.common.FieldsHelper import scroll_to_element
from src.ui.dataViewer import SettingsSignals

from src.ui.modelBuilder import supervised as supervised
from src.ui.modelBuilder import scaler as scaler
from src.ui.common import BannerWidget
from src.ui.common import DirectorySelectorWidget


class SummariesWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    run_summeries_value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)
    model_summary_banner_signal = pyqtSignal(object, bool, str)
    python_files_selector = "Python files (*.py)"

    def __init__(self, scroll):
        super().__init__()
        self.config: ModelBuilderConfig = Config.get(ModelBuilderConfig)
        singals = SettingsSignals(
            value_changed=self.value_changed, show_modal=self.show_modal
        )

        self._value = SummaryModel(**self.config.summaries.__dict__)
        self.value_original = SummaryModel(**self.config.summaries.__dict__)

        self.evaluate_widget = MeasurementWidget(
            self._value.evaluate,
            label="Evaluate model",
            tooltip="Display in console model computed losses and accuracy on the test set.",
            value_changed=singals.value_changed,
        )
        self.roc_curve_widget = MeasurementWidget(
            self._value.roc_curve,
            label="ROC curve",
            tooltip="Receiver Operating Characteristic curve, plots sensitivity against false positive rate.",
            value_changed=singals.value_changed,
        )
        self.prec_recall_curve_widget = MeasurementWidget(
            self._value.prec_recall_curve,
            label="Precision recall curve",
            tooltip="Plots prediction precision against the recall",
            value_changed=singals.value_changed,
        )
        self.f1_score_widget = MeasurementWidget(
            self._value.f1_score,
            label="F-1 score curve",
            tooltip="Harmonic mean of precision and recall showing best tradeoff between precision and recall",
            value_changed=singals.value_changed,
        )
        self.confusion_matrix_widget = MeasurementWidget(
            self._value.confusion_matrix,
            label="Confusion matrix",
            tooltip="Plots per-class performance of the trained model.",
            value_changed=singals.value_changed,
        )
        self.thresholds_widget = LabelValueWidget(
            "Thresholds",
            self._value.thresholds,
            singals,
            tooltip="Prints characteristics like f1, precision, recall, samples count left for specific threshold. When only one threshold set shows additional confusion matrix for given results.",
            val_type=list[float],
            margins=(10, 10, 0, 0),
            bottom=0,
            top=1,
            decimals=4,
        )
        self.size_summary_widget = MeasurementWidget(
            self._value.size_summary,
            label="Size summary",
            tooltip="Shows size histogram on the train set.",
            value_changed=singals.value_changed,
            children=[],
        )
        self.model_name_widget = LabelValueWidget(
            "",
            self._value.diff_model_name,
            singals,
            val_type=str,
            suffix_label=self.config.get_model_ending(),
            margins=(0, 0, 0, 0),
        )
        self.diff_model_name_widget = MeasurementWidget(
            self._value.diff_model_name != None,
            label="Compare against another model",
            tooltip="To compare model name. Ability to compare currently trained model with another model. <br/>\
                <b>Note</b>: to compare models they have to be trained on the same input modalities and same pollen types (ordered in the same way). <br/>\
                <b>Note2</b>: compare models with the same test set size (param: Test model name)",
            value_changed=singals.value_changed,
            children=[self.model_name_widget],
        )
        self.model_summary_banner_widget = BannerWidget(type="Warning")
        self.is_banner_visible = False
        self.summaries_widget = MeasurementWidget(
            self.config.summaries.run_summaries,
            label="Run summaries",
            tooltip="Trained model efficiency on the test set.",
            value_changed=self.run_summeries_value_changed,
            children=[
                self.model_summary_banner_widget,
                self.evaluate_widget,
                self.roc_curve_widget,
                self.prec_recall_curve_widget,
                self.f1_score_widget,
                self.confusion_matrix_widget,
                self.thresholds_widget,
                self.size_summary_widget,
                self.diff_model_name_widget,
            ],
            callbacks={
                self.model_summary_banner_widget: lambda show: self.is_banner_visible
            },
            layout="Vertical",
        )
        self.model_summary_banner_signal.connect(
            lambda obj, is_visible, text: self.set_banner_visbility(
                obj, is_visible, text=text
            )
        )
        self.run_summeries_value_changed.connect(
            lambda obj, changed: scroll_to_element(
                self, scroll, self.summaries_widget.value
            )
        )
        self.run_summeries_value_changed.connect(
            lambda obj, changed: self.model_summary_banner_widget.show_hide_whole_banner(
                self.summaries_widget.value
            )
        )
        self.run_summeries_value_changed.connect(
            lambda obj, changed: self.value_changed.emit(obj, changed)
        )

        self.model_summary_banner_widget.show_hide_whole_banner(
            self.summaries_widget.value
        )

        layoutV = QVBoxLayout()
        layoutV.addWidget(self.summaries_widget)
        layoutV.setAlignment(Qt.AlignTop)
        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        layoutV.setSizeConstraint(QLayout.SetMinimumSize)

    def set_banner_visbility(self, obj, is_visible, text):
        self.is_banner_visible = is_visible
        self.model_summary_banner_widget.show_hide_banner(obj, is_visible, text)

    @property
    def value(self):
        if self.summaries_widget.value == True:
            self._value.run_summaries = True
            self._value.evaluate = self.evaluate_widget.value
            self._value.roc_curve = self.roc_curve_widget.value
            self._value.prec_recall_curve = self.prec_recall_curve_widget.value
            self._value.f1_score = self.f1_score_widget.value
            self._value.confusion_matrix = self.confusion_matrix_widget.value
            self._value.thresholds = self.thresholds_widget.value
            self._value.size_summary = self.size_summary_widget.value
            self._value.diff_model_name = (
                self.model_name_widget.value
                if self.diff_model_name_widget.value == True
                else None
            )
        else:
            self._value = self.value_original
            self._value.run_summaries = False

        return self._value

    @value.setter
    def value(self, value):
        self._value = value
