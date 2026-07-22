#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

from src.core.types.primitives.Float import Float


def parse_str_to_int(s: str):
    if type(s) is str and not s.isdigit():
        raise ValueError(f"Unable to convert string='{s}' to int")

    return int(s)


def parse_float(value, throw_on_none=True) -> Float:
    if type(value) is str:
        return parse_str_to_float(value)
    elif value is None and not throw_on_none:
        return None

    return Float(float(value))


def parse_str_to_float(s: str, prop_name=None) -> Float:
    s = s.replace(",", ".")
    if not str.isdigit(s.replace(".", "").replace("-", "")):
        if prop_name:
            raise ValueError(
                "Given property='%s' is not an int, property value='%s'"
                % (prop_name, s)
            )
        else:
            raise ValueError(f"Given value='{s}' is not an float")

    return Float(float(s))
