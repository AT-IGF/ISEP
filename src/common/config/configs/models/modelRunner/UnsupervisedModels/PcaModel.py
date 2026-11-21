from dataclasses import dataclass


@dataclass
class PcaModel:
    """Currently not supported. Principal Component Analysis dimensional reduction."""

    key: str = None
    components: int | float = 0
