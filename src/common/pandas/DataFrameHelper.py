import logging

import pandas as pd
from io import StringIO

from src.core import write_data, PathHelper, AccessType


def write_data_frame_to_csv(
    path: str, data: dict, add_header=True, access_type: AccessType = AccessType.Access
):
    results = pd.DataFrame(data)
    s = StringIO()
    results.to_csv(s, header=add_header, index=False, lineterminator="\n")
    write_data(
        path=PathHelper.set_path_extension(path, ".csv"),
        new_line_on_access=False,
        data=s.getvalue(),
        access_type=access_type,
    )

    logging.getLogger().debug(f"Saved under path='{path}:'\n{results.to_string()}")
