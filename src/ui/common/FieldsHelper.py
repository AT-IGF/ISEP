import re
import ast
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QValidator
from src.common import Consts
from src.ui.common.NullableIntValidator import StrValidator

_suppress_show = True
def toogle_field_visibility(field, show: bool):
    if show:
        field.setAttribute(Qt.WA_DontShowOnScreen, _suppress_show) # workaround for blinking windows on app load
        field.show()
    else:
        field.hide()


def toogle_fields_visibility(fields, show: bool, callbacks: dict = {}):
    """
    show/hide all elements, when show all check if callback exists and then decide to show/hide child based on callback
    """
    for field in fields:
        if field in callbacks.keys():
            toogle_field_visibility(field, callbacks[field](show))
        else:
            toogle_field_visibility(field, show)


def is_valid_path(path: str):
    return path != "" or path.startswith(Consts.RESOURCES_PATH)


def map_check_state(value: bool):
    if value == True:
        return Qt.CheckState.Checked
    return Qt.CheckState.Unchecked


def map_check_state_to_bool(value: Qt.CheckState):
    if value == Qt.CheckState.Checked or value == True:
        return True
    return False


def on_number_field_edit_finish(
    self, prop, field, validator, show_modal, val_type=None, nullable=False
):
    value = field.text()
    if value == "" and nullable == False and (val_type == int or val_type == float):
        value = str(0)
    value_validator = validator.validate(value, 0)[0]
    _validator = validator
    if (
        hasattr(validator, "inner_validator") == True
    ):  # nasted validator exists, e.g. ListNumberValidator having inner validators like list[QIntValidator]
        _validator = validator.inner_validator
    if value_validator != QValidator.Acceptable:
        if hasattr(validator, "error_message"):
            show_modal.emit(validator.error_message)
        else:
            show_modal.emit(
                f"Field value is invalid.\nAllowed range=[{_validator.bottom()}, {_validator.top()}]"
            )
        original_value = getattr(self, prop)
        field.setText("" if original_value is None else str(original_value))
        return

    old_val = getattr(self, prop)
    tp = val_type
    if val_type == None:
        tp = type(old_val)
    if nullable == True and value.strip() == "":
        new_val = None
    elif nullable == True and tp == float | None:
        new_val = float(value)
    elif nullable == True and tp == int | None:
        new_val = int(value)
    elif tp == list[int] or tp == list[float]:
        ast_vals = ast.literal_eval(value)
        if len(ast_vals) == 0:
            new_val = []
        elif tp == list[int]:
            new_val = [int(p) for p in ast.literal_eval(value)]
            value = str(new_val)
        elif tp == list[float]:
            new_val = [float(p) for p in ast.literal_eval(value)]
            value = str(new_val)
    else:
        new_val = tp(value)  # convert incoming to same type as attr

    field.setText("" if value is None else value)
    setattr(self, prop, new_val)


def emit_on_change(field, old_value, event):
    def event_callback():
        if field.text() == "" and old_value == None:
            event.emit(field, False)
        elif field.text() != str(old_value):
            event.emit(field, True)
        else:
            event.emit(field, False)

    field.editingFinished.connect(lambda: event_callback())


def scroll_to_element(element, scroll, should_scroll=True):
    if should_scroll == True:
        QTimer.singleShot(0, lambda: scroll.ensureWidgetVisible(element))
