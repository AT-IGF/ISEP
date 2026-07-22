#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw


def is_blank(s) -> bool:
    """
    Returns True if string is: None, empty, contains spaces
    :param s:
    :return:
    """
    return not bool(s and not s.isspace())
