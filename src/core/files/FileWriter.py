#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

import logging
import os
from typing import Any

from src.core.files.models.FileAccessType import AccessType
from src.core.path.PathHelper import PathHelper
from src.core.parsers.stringParsers.Strings import is_blank


def write_data_list(
    path: str,
    data: list[Any],
    access_type: AccessType = AccessType.Access,
    new_line_on_access: bool = True,
    append_none_or_empty: bool = True,
    separator: str = "\n",
):
    write_data(
        path=path,
        data=separator.join(str(x) for x in data),
        access_type=access_type,
        new_line_on_access=new_line_on_access,
        append_none_or_empty=append_none_or_empty,
    )


def write_data(
    path,
    data,
    access_type: AccessType = AccessType.Access,
    new_line_on_access=True,
    append_none_or_empty=True,
):
    if access_type == AccessType.Access and not PathHelper.is_file_exists(path):
        access_type = AccessType.Write

    if not append_none_or_empty and is_blank(data):
        logger = logging.getLogger()
        logger.warning(f"Saving skipped, no data to save, file='{path}'")
        return

    if new_line_on_access and access_type == AccessType.Access:
        data = "\n" + data

    dirs = PathHelper.get_dirs(path)
    if not PathHelper.is_file_exists(dirs):
        os.makedirs(dirs)

    f = open(path, access_type.value)
    f.write(data)
    f.close()
