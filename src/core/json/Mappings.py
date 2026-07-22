import json

from src.core.path import PathHelper


def get_list_int_mapping(mapping_path, ref_keys, key_type=int, is_list=True):
    if not PathHelper.is_exists(mapping_path):
        raise ValueError(f"Mapping path does not exists, path={mapping_path}")
    with open(mapping_path) as f:
        mapping = json.load(f)
    if not isinstance(mapping, dict):
        raise ValueError("Mapping must be a dict")
    for key, value in mapping.items():
        if ref_keys is not None and key not in ref_keys:
            raise ValueError(
                f"Mapping key does not exists in configured keys, key={key}, configured_keys={ref_keys}"
            )
        if is_list:
            if not isinstance(value, list):
                raise ValueError(
                    f"Mapping value for key is not a list, key={key}, value={value}"
                )
            if not all(isinstance(item, key_type) for item in value):
                raise ValueError(
                    f"Mapping value for key contains non-{key_type} elements, key={key}, value={value}"
                )
        else:
            if not isinstance(value, key_type):
                raise ValueError(
                    f"Mapping value for key is not a {key_type}, key={key}, value={value}"
                )
        return mapping
