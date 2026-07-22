from dataclasses import dataclass
from datetime import datetime
from src.core import File, PathHelper


@dataclass
class FilesToProcess:
    files: list[File]
    date: str
    progress_file_path: str
    output_dir: str
    output_file_extension: str
    is_partially_processed: bool
