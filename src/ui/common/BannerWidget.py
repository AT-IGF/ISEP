from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame

from src.ui.common import IconLabel
from PyQt5.QtGui import QColor

from src.ui.common.FieldsHelper import toogle_field_visibility
from src.ui.common.Banner import MessageModel
from src.core import is_blank


class BannerWidget(QWidget):
    value_changed = pyqtSignal(object, bool)
    show_modal = pyqtSignal(object)

    WARNING = "Warning"
    TYPES = [WARNING]

    def __init__(self, type):
        super().__init__()
        self._messages: dict[object, MessageModel] = {}
        self._is_whole_banner_visible = True

        if type == self.WARNING:
            colors = "#8A8A00"
        else:
            raise NotImplementedError(
                f"Banner type not implemented, type={type}, allowed_types=[{', '.join(self.TYPES)}]"
            )

        container_wrapper_layout = QVBoxLayout()
        container = QFrame()
        container.setObjectName("warningContainer")
        container.setStyleSheet(
            f"""
        QFrame#warningContainer {{
            background-color: white;
            border: 2px solid {colors};
            border-radius: 4px;
            }}
        """
        )
        warning_layoutH = QHBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("bannerLabel")
        self.label.setStyleSheet(
            "color: #8A8A00; font-weight: bold; font-size: 16px; text-align: center;"
        )
        self.label.setWordWrap(True)
        file_exists_warning_icon = IconLabel(
            "mdi.alert-outline", color=QColor(colors), size=24
        )
        warning_layoutH.addWidget(file_exists_warning_icon)
        warning_layoutH.addWidget(self.label, stretch=1)
        warning_layoutH.setContentsMargins(10, 10, 10, 10)
        container.setLayout(warning_layoutH)
        container_wrapper_layout.addWidget(container)
        container_wrapper_layout.setContentsMargins(0, 20, 0, 0)
        self.setLayout(container_wrapper_layout)

    def setText(self, text):
        self.label.setText(text)

    def get_messages_to_show(self):
        to_show_messages: list = []
        for message in self.messages.values():
            if message.is_visible and not is_blank(message.text):
                to_show_messages.append(message.text)
        if len(to_show_messages) == 1:
            return to_show_messages[0]

        return "".join(f"- {message}\n" for message in to_show_messages)

    def show_hide_messages(self):
        if self._is_whole_banner_visible == False:
            toogle_field_visibility(self, show=False)
            return

        messages_to_show = self.get_messages_to_show()
        if is_blank(messages_to_show):
            toogle_field_visibility(self, show=False)
        else:
            self.setText(messages_to_show)
            toogle_field_visibility(self, show=True)

    def show_hide_banner(self, obj, is_visible, text=None):
        if obj is None:
            raise ValueError("Object cannot be None")

        self.messages[obj] = MessageModel(obj=obj, is_visible=is_visible, text=text)

        self.show_hide_messages()

    def show_hide_whole_banner(self, is_visible):
        self._is_whole_banner_visible = is_visible
        self.show_hide_messages()

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, value):
        self._messages = value

    def set_message(self, obj, message: str):
        if message == None or str(message).strip() == "":
            return
        self._messages[obj] = message
