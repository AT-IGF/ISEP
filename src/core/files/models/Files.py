#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

import os
from typing import List

from src.core.files.models.File import File


class Files:
    def __init__(self):
        self._files: List[File] = []

    _paths = []

    @property
    def files(self) -> List[File]:
        return self._files

    @files.setter
    def files(self, value: list):
        if not isinstance(value, list):
            raise ValueError("Given files is not a list type.")
        self._files = value

    def append_file(self, value: File):
        if not isinstance(value, File):
            raise ValueError("Given files is not a File type.")
        self._files.append(value)

    def get_file_paths(self):
        if len(self._paths) == 0 and any(self._files):
            for file in self._files:
                self._paths.append(os.path.join(file.path, file.filename))

        return self._paths

    def append_whole_file_path(self, file_path: str):
        if not isinstance(file_path, str):
            raise ValueError("Given file path is not a string type.")
        head, tail = os.path.split(file_path)
        self._files.append(File(filename=tail, path=head))
