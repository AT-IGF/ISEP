#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

import os


def get_file_lines(path, lines_to_ignore_prefix: str | None = None):
    if not os.path.exists(path):
        return []

    if lines_to_ignore_prefix is not None:
        with open(path) as file:
            return [line.rstrip() for line in file if not line.rstrip().startswith(lines_to_ignore_prefix)]

    with open(path) as file:
        return [line.rstrip() for line in file]


def filer_file_lines(path: str, phrase: str):
    lines = []
    with open(path) as file:
        for line in file:
            line_clean = line.rstrip()
            if phrase is not None and phrase in line_clean:
                lines.append(line_clean)

    return lines
