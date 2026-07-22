#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

import os
from pathlib import Path

from src.core.files.LinesHelper import get_file_lines


class File:
    def __init__(self, filename=None, path=None):
        if filename is None and path is not None:
            head, tail = os.path.split(path)
            self._filename = tail
            self._path = head
        else:
            self._filename = filename
            self._path = path
        self._lines = None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value: str):
        if not isinstance(value, str):
            raise ValueError(f"Filename is not a str. Value='{value}'")
        self._filename = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Path is not a str.")
        self._path = value

    def get_file_path(self):
        if self._path is None or self._filename is None:
            raise ValueError("Path or filename is not defined.")
        return os.path.join(self._path, self._filename)

    def get_file_name_no_extension(self):
        if self._filename is None:
            raise ValueError("Filename is not defined.")
        return Path(self._filename).stem

    def lines(self, lines_to_ignore_prefix: str | None = None):
        """
        Not suggested to handle large files. It may produce memory out of range exception.
        In large files better way is to read file line by line.
        """
        if self._lines is None:
            self._lines = get_file_lines(self.get_file_path(), lines_to_ignore_prefix)

        return self._lines
