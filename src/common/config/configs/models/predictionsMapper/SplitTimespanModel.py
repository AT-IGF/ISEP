from dataclasses import dataclass
from datetime import datetime

from src.common import Consts


@dataclass()
class SplitTimespanModel:
    timestamp_column_name = Consts.TIMESTAMP_COLUMN_NAME
    range_from: datetime | None = None
    range_to: datetime | None = None
    days: int = 7
    hours: int = 0
    minutes: int = 0
    seconds: int = 0

    def __post_init__(self):
        if self.range_from and self.range_to:
            if self.range_from > self.range_to:
                raise ValueError("range_from must be before range_to")

    def is_below_from_range(self, value):
        if self.range_from is None:
            return False
        return value < self.range_from

    def is_above_to_range(self, value):
        if self.range_to is None:
            return False
        return value > self.range_to

    def is_range_set(self):
        return self.range_from is not None or self.range_to is not None

    def range_to_text(self):
        if self.range_to is None:
            return "+∞"
        else:
            return self.range_to

    def range_from_text(self):
        if self.range_from is None:
            return "-∞"
        else:
            return self.range_from
