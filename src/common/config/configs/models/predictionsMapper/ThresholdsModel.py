from dataclasses import dataclass

from src.core.json.Mappings import get_list_int_mapping


@dataclass
class ThresholdsModel:
    COMMON_THRESHOLD = "COMMON_THRESHOLD"
    CLASS_THRESHOLD = "CLASS_THRESHOLD"

    threshold_type: str = COMMON_THRESHOLD
    threshold: float = 0.2
    per_type_thresholds_path: str | None = None

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

        mapping = get_list_int_mapping(
            mapping_path=self.per_type_thresholds_path,
            ref_keys=None,
            key_type=float,
            is_list=False,
        )
        setattr(self, path_attr, self.per_type_thresholds_path)
        setattr(self, mapping_attr, mapping)
        return mapping
