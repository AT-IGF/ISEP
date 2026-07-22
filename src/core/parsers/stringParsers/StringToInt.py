#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

import itertools

from src.core.types.primitives.Int import Int


def index_of(val, in_list):
    try:
        return in_list.index(val)
    except ValueError:
        return -1


def substring(s, start, stop):
    return s[start:stop]


def try_int_sequence_from_string(filename: str, format, chars_searched):
    if chars_searched not in format:
        raise ValueError(
            "Chars '{}' to find in format '{}' not found".format(chars_searched, format)
        )

    string_int_list = [
        "".join(x) for _, x in itertools.groupby(filename, key=str.isdigit)
    ]
    formats_found = [
        len(item) == len(format) and item.isdigit() for item in string_int_list
    ]
    format_index = index_of(True, formats_found)
    if format_index == -1:
        return None

    chars_index = index_of(chars_searched, format)
    sequence = substring(
        s=string_int_list[format_index],
        start=chars_index,
        stop=chars_index + len(chars_searched),
    )

    return int(sequence)


def try_int_sequence_from_string_by_chars(filename: str, format, chars_searched) -> Int:
    if chars_searched not in format:
        raise ValueError(
            "Chars '{}' to find in format '{}' not found".format(chars_searched, format)
        )

    searched_index = index_of(chars_searched, format)
    searched_len = len(chars_searched)

    sequence = substring(
        s=filename, start=searched_index, stop=searched_index + searched_len
    )
    if not sequence.isdigit():
        raise ValueError("Searched value is not an int.")

    return Int(int(sequence))


def split_by_every_nth_char(s: str, chars_len: int, delegate_func):
    return [delegate_func(s[i : i + chars_len]) for i in range(0, len(s), chars_len)]
