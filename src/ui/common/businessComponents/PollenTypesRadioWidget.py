import logging
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt

from src.common.config import Config
from src.common.config.configs import TypesConfig
from src.ui.common.LabelValueWidget import LabelValueWidget
from src.ui.dataViewer.SettingsSignals import SettingsSignals
from src.ui.dataViewer import aggregatedSamples as aggregated
from src.ui.common.businessComponents.PollenTypesWidget import PollenTypesWidget


class PollenTypesRadioWidget(QWidget):
    SHOW_ALL_OPTION = "SHOW_ALL"
    SELECTED_OPTION = "SELECTED"
    EXCLUDE_OPTION = "EXCLUDE"
    ONLY_ONE_OPTION = "ONLY_ONE"

    def __init__(
        self,
        singals: SettingsSignals,
        options: list[str] = [
            SHOW_ALL_OPTION,
            SELECTED_OPTION,
            EXCLUDE_OPTION,
            ONLY_ONE_OPTION,
        ],
        preselected_option: str = None,
        pollen_types_to_exclude: list[str] = [],
        pollen_types: list[str] = [],
        show_only: str = "",
        tooltip=None,
        margins=None,
    ):
        super().__init__()
        if len(options) == 0:
            logging.getLogger("ui").debug(
                "No option added for PollenTypesWidget, widget will not be displayed"
            )
            return

        self.single_type_widget = LabelValueWidget(
            label="Pollen type name:",
            tooltip="",
            value=show_only,
            val_type=str,
            singals=singals,
            margins=(20, 10, 0, 0),
        )

        self.pollen_types_widget = PollenTypesWidget(
            pollen_types,
            signals=singals,
            include_only=[
                PollenTypesWidget.GENERAL_ALIGN_OPTION,
                PollenTypesWidget.ADD_OPTION,
                PollenTypesWidget.REMOVE_OPTION,
                PollenTypesWidget.MOVE_OPTION,
                PollenTypesWidget.RESET_OPTION,
            ],
            margins=(10, 10, 0, 0),
        )

        self.pollen_types_exclude_widget = PollenTypesWidget(
            pollen_types_to_exclude,
            signals=singals,
            include_only=[
                PollenTypesWidget.GENERAL_ALIGN_OPTION,
                PollenTypesWidget.ADD_OPTION,
                PollenTypesWidget.REMOVE_OPTION,
                PollenTypesWidget.MOVE_OPTION,
                PollenTypesWidget.RESET_OPTION,
            ],
            label="Pollen types to exclude",
            show_no_types_error=False,
            margins=(10, 10, 0, 0),
        )

        preselected = options[0]
        if preselected_option != None and preselected_option in options:
            preselected = preselected_option

        sub_apps = []
        if self.SHOW_ALL_OPTION in options:
            all_option = aggregated.Radio("ALL", preselected, None, label="Show all")
            sub_apps.append(all_option)
        if self.SELECTED_OPTION in options:
            specific_options = aggregated.Radio(
                self.SELECTED_OPTION,
                preselected,
                self.pollen_types_widget,
                label="Show selected",
            )
            sub_apps.append(specific_options)
        if self.EXCLUDE_OPTION in options:
            exclude_option = aggregated.Radio(
                "EXCLUDE",
                "EXCLUDE",
                self.pollen_types_exclude_widget,
                label="Exclude types",
            )

            sub_apps.append(exclude_option)
        if self.ONLY_ONE_OPTION in options:
            show_only_option = aggregated.Radio(
                "ONLY_ONE",
                preselected,
                self.single_type_widget,
                label="Show only one type",
            )
            sub_apps.append(show_only_option)

        self.types_widget = aggregated.RadioSelectorWidget(
            self,
            sub_apps,
            singals.value_changed,
            label="Types to show:",
            tooltip=tooltip,
            layout="Horizontal",
            margins=(0, 0, 0, 0),
            is_white_background=False,
            sub_widgets_layout="Below",
        )

        layoutV = QVBoxLayout()
        layoutV.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        if margins != None:
            layoutV.setContentsMargins(*margins)  # left, top, right, bottom
        layoutV.addWidget(self.types_widget)
        layoutV.setSpacing(0)
        layoutV.addStretch(1)
        layoutV.setAlignment(Qt.AlignTop)
        self.setLayout(layoutV)

    def get_selection(self, pollen_types=None):
        return {
            "selected": self.types_widget.selected_app.value,
            "options": {
                self.SHOW_ALL_OPTION: self.get_all_option(pollen_types),
                self.SELECTED_OPTION: self.pollen_types_widget.get_types(),
                self.EXCLUDE_OPTION: self.pollen_types_exclude_widget.get_types(),
                self.ONLY_ONE_OPTION: self.single_type_widget.value,
            },
        }

    def get_all_option(self, pollen_types=None):
        if pollen_types == None:
            pollen_types = Config.get(TypesConfig).pollen_types

        if self.types_widget.selected_app.value == self.SHOW_ALL_OPTION:
            return pollen_types

        return None

    def get_selected_option(self):
        if self.types_widget.selected_app.value == self.SELECTED_OPTION:
            return self.pollen_types_widget.get_types()
        return []

    def get_excluded_option(self):
        if self.types_widget.selected_app.value == self.EXCLUDE_OPTION:
            return self.pollen_types_exclude_widget.get_types()

        return []

    def get_single_option(self):
        if self.types_widget.selected_app.value == self.ONLY_ONE_OPTION:
            return self.single_type_widget.value

        return None

    def remove_items(items, to_exclude):
        return [x for x in items if x not in to_exclude]
