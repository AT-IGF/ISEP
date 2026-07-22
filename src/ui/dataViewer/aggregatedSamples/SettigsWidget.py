from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal

from src.common.config import Config
from src.common.config.configs import TypesConfig
from src.common.config.configs import AllParticlesAvgsConfig
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.common.MeasurementWidget import MeasurementWidget
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.common.businessComponents.PollenTypesWidget import PollenTypesWidget
from src.ui.common.businessComponents.FilterWidget import FilterWidget


class SettigsWidget(QWidget):
    value_changed = pyqtSignal(object, bool)

    def __init__(self, config: AllParticlesAvgsConfig, singals: SettingsSignals):
        super().__init__()

        self.signals = SettingsSignals(
            value_changed=self.value_changed, show_modal=singals.show_modal
        )
        self.value_changed.connect(
            lambda obj, value: singals.value_changed.emit(obj, value)
        )

        self.pollen_types_widget = PollenTypesWidget(
            pollen_types=config.pollen_types,
            signals=self.signals,
            include_only=[
                PollenTypesWidget.GENERAL_ALIGN_OPTION,
                PollenTypesWidget.ADD_OPTION,
                PollenTypesWidget.REMOVE_OPTION,
                PollenTypesWidget.RESET_OPTION,
            ],
            show_no_types_error=False,
            label="Pollen types to show",
            tooltip="Labeled samples directories that will not take part in the training",
        )
        self.filter_widget = FilterWidget(
            filter_path=config.filter_path, singals=self.signals, margins=(10, 0, 0, 0)
        )
        self.single_type_count_widget = LabelValueWidget(
            label="Same type count",
            tooltip="Number of the same type pollen particles.<br/><b>Note</b>: Given value describes number of samples before potential filtering.",
            value=config.single_type_count,
            singals=singals,
            val_type=int | None,
            margins=(20, 10, 0, 0),
            bottom=1,
        )

        layoutV = QVBoxLayout()
        layoutV.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        layoutV.addWidget(self.pollen_types_widget)
        layoutV.addWidget(self.filter_widget)
        layoutV.addWidget(self.single_type_count_widget)
        layoutV.setSpacing(0)
        layoutV.addStretch(1)
        layoutV.setAlignment(Qt.AlignTop)
        self.setLayout(layoutV)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

    def get_pollen_types_to_exclude(self, all_types=None):
        return self.pollen_types_widget.get_pollen_types_to_exclude()
