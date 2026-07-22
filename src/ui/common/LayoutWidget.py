from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt5.QtCore import Qt

from src.ui.common.Helpers.TooltipHelper import add_tooltip_or_text_to_layout


class LayoutWidget(QWidget):
    def __init__(
        self,
        children: list,
        layout_type="H",
        margins=None,
        spacing=None,
        float_left=True,
        label_tooltip: tuple[str, str] | None = None,
    ):
        super().__init__()

        if layout_type == "H":
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()

        if label_tooltip is not None:
            (label_value, tooltip_value) = label_tooltip
            label = QLabel(label_value)
            layout.addWidget(label)
            add_tooltip_or_text_to_layout(
                tooltip=tooltip_value, label_widget=label, layout=layout, spacer=False
            )

        [layout.addWidget(child) for child in children]
        layout.setSpacing(0)
        if spacing != None:
            layout.setSpacing(spacing)

        layout.setContentsMargins(10, 10, 0, 0)  # left, top, right, bottom
        if margins != None:
            layout.setContentsMargins(*margins)  # left, top, right, bottom

        if float_left:
            layout.addStretch(1)
        self.setLayout(layout)
