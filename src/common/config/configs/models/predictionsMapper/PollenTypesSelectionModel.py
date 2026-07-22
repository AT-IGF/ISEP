from dataclasses import dataclass, field
from src.core import is_blank


@dataclass()
class PollenTypesSelectionModel:
    types_to_exclude: list[str] = field(default_factory=list)
    show_only: str | None = None

    def is_show_only_option(self):
        if is_blank(self.show_only):
            return False
        return True
