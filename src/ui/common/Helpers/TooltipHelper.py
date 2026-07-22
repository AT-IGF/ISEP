from src.ui.common import IconLabel
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from src.core import is_blank


def add_tooltip_or_text_to_layout(
    tooltip, label_widget, layout, suffix_text=":", spacer=False
):
    label_text = label_widget.text().strip()
    is_tooltip = tooltip != None and tooltip.strip() != ""
    if is_tooltip:
        if not is_blank(label_text):
            label_widget.setText(label_text)  # remove empty spaces
        if not is_blank(suffix_text) and label_text.endswith(suffix_text):
            label_widget.setText(label_text.removesuffix(suffix_text))
        plot_spectrum_help = IconLabel(
            "mdi.help-circle-outline",
            tooltip=tooltip,
            color="darkBlue",
            text=suffix_text,
        )
        layout.addWidget(plot_spectrum_help)
    elif not is_blank(label_text) and not label_text.endswith(suffix_text):
        label_widget.setText(label_text + suffix_text)
    if spacer == True:
        spacer_widget = QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        layout.addItem(spacer_widget)
