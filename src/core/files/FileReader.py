#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

import os
import ntpath

from netCDF4 import Dataset

from src.core.files.models.File import File
from src.core.files.models.FileAccessType import AccessType
from src.core.files.models.Files import Files
from src.core.path.PathHelper import PathHelper


def read_file_by_path(path):
    head, tail = ntpath.split(path)
    file = File()
    file.path = head
    file.filename = tail
    return file


def read_dataset(path, extension=""):
    _files = Files()
    if not PathHelper.is_file_exists(path):
        raise FileNotFoundError(f"Directory not found, directory: '{path}'")
    for root, dirs, files in os.walk(path):
        for file in files:
            if extension in file:
                _file = File()
                _file.path = root
                _file.filename = file
                _files.append_file(_file)

    return _files


def read_nc_file(file: File, access_type: AccessType = AccessType.Read):
    at_value = access_type.value
    if not access_type.has_value(at_value):
        raise ValueError(
            str.format("No such access type(%s) for opening NcFile" % at_value)
        )
    return Dataset(file.get_file_path(), access_type.value)
