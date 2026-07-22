#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

from src.core.files.models.File import File


def get_files_filenames(files: list[File]):
    return [f.filename for f in files if f is not None and f.filename is not None]


def get_filenames_joined(files: list[File], separator: str) -> str:
    filenames = get_files_filenames(files)
    return separator.join(filenames)
