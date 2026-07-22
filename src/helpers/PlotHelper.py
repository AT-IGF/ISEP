from src.common import Consts


def should_be_displayed(pollen_types: list[str], p_type):
    return p_type in pollen_types


def get_name(val):
    if val not in Consts.FOLDER_NAME_MAPPING.keys():
        return val
    return Consts.FOLDER_NAME_MAPPING[val]
