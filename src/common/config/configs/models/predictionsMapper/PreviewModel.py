from dataclasses import dataclass


@dataclass
class PreviewModel:
    """Preview settings for quick looks at large prediction files."""

    keep_every_nth_row: int | None = None
    """Sample interval. Keep every n-th line of the processed file. Allows to reduce the number of
    processed samples for quick looks. Particle counts and concentrations are not rescaled, so they are
    about n times lower than for the whole file. ``None`` or 0 disables the option."""

    def is_row_skipping_enabled(self):
        return self.keep_every_nth_row is not None and self.keep_every_nth_row > 0

    def get_keep_every_nth_row(self):
        if self.keep_every_nth_row is None:
            return 0
        return self.keep_every_nth_row
