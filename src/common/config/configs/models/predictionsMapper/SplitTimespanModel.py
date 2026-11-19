from dataclasses import dataclass
from datetime import datetime

from src.common import Consts


@dataclass()
class SplitTimespanModel:
    """Time spans in which particle counts are summed."""

    timestamp_column_name = Consts.TIMESTAMP_COLUMN_NAME

    range_from: datetime | None = None
    """Start of the date time range between which data will be processed (inclusive). Note: the file to
    process is read as a whole; the range is applied in further steps."""

    range_to: datetime | None = None
    """End of the date time range between which data will be processed (inclusive). Has to be later than
    ``range_from``."""

    days: int = 7
    """Days of the time span into which measurements are grouped."""

    hours: int = 0
    """Hours of the time span into which measurements are grouped."""

    minutes: int = 0
    """Minutes of the time span into which measurements are grouped."""

    seconds: int = 0
    """Seconds of the time span into which measurements are grouped. A time span starts at the first
    particle after the previous span ends, so spans are not aligned to calendar boundaries (e.g. midnight).
    When all time span values are 0, each result is shown separately."""

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
