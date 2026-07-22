from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from src.ui.common import (
    MeasurementWidget,
    DirectorySelectorWidget,
)
from src.core import PathHelper
from src.common import Consts
from src.ui.common import BannerWidget


class ScalerWidget(QWidget):
    SCALER_NOT_SET_WARNING = "Scaler is not set, create it via Model builder -> Scaler"
    SCALER_INVALID_PATH_WARNING = "Scaler path is invalid and will be not set, select it or create via Model builder -> Scaler"

    scaler_value_changed = pyqtSignal(object, bool)

    def __init__(
        self,
        scaler_path,
        value_changed,
        show_modal,
        banner_widget: BannerWidget,
        margins=None,
    ):
        super().__init__()
        self.scaler_path = scaler_path
        self.value_changed = value_changed
        self.show_modal = show_modal
        self.banner_widget = banner_widget

        self.scaler_path_widget = DirectorySelectorWidget(
            "Scaler path",
            scaler_path,
            tooltip="Fitted scaler file path form the Scaler tab.",
            value_changed=value_changed,
            show_modal=self.show_modal,
            selector="FILE",
            extensions=DirectorySelectorWidget.SCALER_EXTENSION,
            margins=(10, 0, 0, 0),
        )
        # self.scaler_widget = MeasurementWidget(
        #     self.scaler_path_widget.value != None,
        #     label="Scaler path",
        #     tooltip="Fitted scaler file path form the Scaler tab.",
        #     value_changed=self.scaler_value_changed,
        #     children=[self.scaler_path_widget],
        #     layout="Horizontal",
        #     margins=(10, 0, 0, 0),
        #     spacing_children=(0),
        # )

        # self.scaler_widget.value_changed.connect(
        #     lambda: self.show_banner_if_scaler_not_exists()
        # )
        self.scaler_path_widget.value_changed.connect(
            lambda: self.show_banner_if_scaler_not_exists()
        )
        self.show_banner_if_scaler_not_exists()

        layoutV = QVBoxLayout()
        if margins != None:
            layoutV.setContentsMargins(*margins)  # left, top, right, bottom
        self.setLayout(layoutV)

        # layoutV.addWidget(self.scaler_widget)
        layoutV.addWidget(self.scaler_path_widget)
        layoutV.setAlignment(Qt.AlignLeft)
        # layoutV.setSpacing(0)
        # layoutV.addStretch(1)
        self.setLayout(layoutV)

    def is_scaler_exists(self):
        if self.scaler_path_widget.value == None:
            return False

        path = PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.scaler_path_widget.value,
            raise_on_not_found=False,
        )
        return PathHelper.is_file(path)

    def show_banner_if_scaler_not_exists(self):
        # if self.scaler_widget.value == False or self.scaler_path_widget.value == None:
        if self.scaler_path_widget.value == None:
            self.banner_widget.show_hide_banner(
                obj=self.scaler_path_widget,
                is_visible=True,
                text=self.SCALER_NOT_SET_WARNING,
            )
            return

        if self.is_scaler_exists() == True:
            self.banner_widget.show_hide_banner(
                obj=self.scaler_path_widget, is_visible=False
            )
            return

        self.banner_widget.show_hide_banner(
            obj=self.scaler_path_widget,
            is_visible=True,
            text=self.SCALER_INVALID_PATH_WARNING,
        )

    @property
    def value(self):
        # if self.scaler_widget.value == False:
        #     return None

        if not self.is_scaler_exists():
            return None

        return PathHelper.remove_path_base(
            Consts.RESOURCES_PATH, self.scaler_path_widget.value
        )

    @value.setter
    def value(self, value):
        self._value = value
