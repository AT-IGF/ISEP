from dataclasses import dataclass


@dataclass
class PreviewModel:
    keep_every_nth_row: int | None = None

    def is_row_skipping_enabled(self):
        return self.keep_every_nth_row is not None and self.keep_every_nth_row > 0

    def get_keep_every_nth_row(self):
        if self.keep_every_nth_row is None:
            return 0
        return self.keep_every_nth_row
