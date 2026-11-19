from dataclasses import dataclass

from src.common import Consts
from src.core.path import PathHelper
from src.core.json.Mappings import get_list_int_mapping


@dataclass
class ThresholdsModel:
    """Threshold of the highest class probability above which a particle is counted."""

    COMMON_THRESHOLD = "COMMON_THRESHOLD"
    """Single threshold for all types."""

    CLASS_THRESHOLD = "CLASS_THRESHOLD"
    """Per type thresholds."""

    threshold_type: str = COMMON_THRESHOLD
    """Threshold mode. Single threshold for all types (``threshold``) or a separate threshold for every
    pollen type (``per_type_thresholds_path``)."""

    threshold: float = 0.2
    """Threshold at which the summary will be run. A particle is counted if its highest class probability
    reaches the threshold. Used with the single threshold mode; the value is also part of the output file
    name."""

    per_type_thresholds_path: str | None = None
    """Mapping file in JSON format containing the threshold of every pollen type (class), e.g.
    ``{"Alnus": 0.4, "Corylus": 0.2}``. The mapping has to contain exactly the pollen types of the file to
    process. The file should be created by the user; F1 scores from the supervised training summaries can
    serve as a basis."""

    def is_class_threshold(self):
        return self.threshold_type == self.CLASS_THRESHOLD

    def get_threshold(self):
        if self.threshold_type == self.CLASS_THRESHOLD:
            return self.get_thresholds()
        else:
            return self.threshold

    def get_thresholds(self):
        if self.threshold_type != self.CLASS_THRESHOLD:
            return {}

        path_attr = "mapping_path_cache"
        mapping_attr = "mapping_attr"
        if (
            hasattr(self, path_attr)
            and getattr(self, path_attr) == self.per_type_thresholds_path
            and hasattr(self, mapping_attr)
        ):
            return getattr(self, mapping_attr)

        mapping_path = PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.per_type_thresholds_path,
            raise_on_not_found=False,
        )
        mapping = get_list_int_mapping(
            mapping_path=mapping_path,
            ref_keys=None,
            key_type=float,
            is_list=False,
        )
        setattr(self, path_attr, self.per_type_thresholds_path)
        setattr(self, mapping_attr, mapping)
        return mapping
