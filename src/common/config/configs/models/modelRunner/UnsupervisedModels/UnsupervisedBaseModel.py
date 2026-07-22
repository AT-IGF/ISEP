from dataclasses import dataclass


@dataclass
class UnsupervisedBaseModel:
    run: bool = False
    path: str | None = None
    mapping_path: str | None = None
    key: str = None  # ui purposes
