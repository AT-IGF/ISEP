#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

from enum import Enum


class AccessType(Enum):
    Read = "r"
    Write = "w"
    Access = "a"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_