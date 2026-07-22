from PyQt5.QtGui import QIntValidator, QValidator, QDoubleValidator
import ast

from src.common import Consts


class NullableValidator(QValidator):
    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, text: str, pos: int):
        return QValidator.Acceptable, text, pos


class StrValidator(QValidator):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.not_empty = False
        self.error_message = "Invalid value"

        if "requirements" in kwargs:
            if "not_empty" in kwargs["requirements"]:
                self.not_empty = True

    def validate(self, text: str, pos: int):
        if self.not_empty == True:
            if text == None or text.strip() == "":
                self.error_message = "Field cannot be empty"
                return (QValidator.Invalid, text, pos)
        return QValidator.Acceptable, text, pos


class NullableIntValidator(QIntValidator):
    def __init__(self, parent=None, bottom=Consts.INT_MIN, top=2**31 - 1):
        super().__init__(bottom, top, parent)

    def validate(self, input_str: str, pos: int):
        if input_str == "":
            return (QValidator.Acceptable, input_str, pos)
        return super().validate(input_str, pos)


class ListNumberValidator(QValidator):

    def __init__(self, parent=None, val_type: list = [], **kwargs):
        super().__init__(parent)
        self.error_message = f"Field value is invalid.\n\nNote: values should be within the square brackets []"

        if "specific_vals" in kwargs:
            self.specific_vals = kwargs["specific_vals"]
            kwargs.pop("specific_vals", None)
            self.error_message = f"Field value is invalid.\nAllowed values={self.specific_vals}\n\nNote: values should be within the square brackets []"

        if val_type == list[int]:
            if "bottom" not in kwargs:
                kwargs["bottom"] = 0
            if "top" not in kwargs:
                kwargs["top"] = 2**31 - 1
            message_part = (
                f"\nAllowed values: min={kwargs['bottom']}, max={kwargs['top']}"
            )
            self.error_message += message_part
            self.inner_validator = QIntValidator(parent, **kwargs)
        elif val_type == list[float]:
            if "bottom" not in kwargs:
                kwargs["bottom"] = 0.0
            if "top" not in kwargs:
                kwargs["top"] = 1
            if "decimals" not in kwargs:
                kwargs["decimals"] = 10

            message_part = f"\nAllowed values: min={kwargs['bottom']}, max={kwargs['top']}, decimal places={kwargs['decimals']}"
            self.error_message += message_part
            self.inner_validator = QDoubleValidator(parent, **kwargs)

    def validate(self, text: str, pos: int):
        if not text:
            return QValidator.Invalid, text, pos

        try:
            parts = ast.literal_eval(text)
        except Exception:
            return (QValidator.Invalid, text, pos)

        if (
            not isinstance(parts, list) 
            or len(parts) == 0
            and hasattr(self, "specific_vals")
            and self.specific_vals != None
            and len(self.specific_vals) != 0
        ):
            return (QValidator.Invalid, text, pos)

        for i, p in enumerate(parts):
            if hasattr(self, "specific_vals") and p not in self.specific_vals:
                return (QValidator.Invalid, text, pos)
            if p in ("", None):
                return (
                    (QValidator.Intermediate, text, pos)
                    if i == len(parts) - 1
                    else (QValidator.Invalid, text, pos)
                )
            state, _, _ = self.inner_validator.validate(str(p), i)
            if state != QValidator.Acceptable:
                return state, text, pos
        return QValidator.Acceptable, text, pos

    def fixup(self, text: str) -> str:
        # clean up sray commas/spaces
        return ",".join(p for p in (s.strip() for s in text.split(",")) if p)


class AcceptAllValidator(QValidator):
    def validate(self, text: str, pos: int):
        return QValidator.Acceptable, text, pos

    def fixup(self, text: str) -> str:
        return text


class NullableDoubleValidator(QDoubleValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, input_str: str, pos: int):
        if input_str == "":
            return (QValidator.Acceptable, input_str, pos)
        return super().validate(input_str, pos)


def type_validatior(self, val_type, **kwargs):
    if val_type == list[int] or val_type == list[float]:
        return ListNumberValidator(self, val_type, **kwargs)
    if val_type == str and "requirements" in kwargs:
        return StrValidator(self, **kwargs)
    if val_type == str:
        return AcceptAllValidator()
    if val_type == float:
        return QDoubleValidator(**kwargs)
    if val_type == float | None:
        return NullableDoubleValidator(**kwargs)
    if val_type == int:
        return QIntValidator(**kwargs)
    if val_type == int | None:
        return NullableIntValidator(self, **kwargs)

    return NullableValidator(self, **kwargs)
