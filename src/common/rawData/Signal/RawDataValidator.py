from .RawDataKeys import VAL_SCATTERING, VAL_SCATTERING_IMAGE, VAL_SPECTROMETER, VAL_LIFETIME, VAL_TIMESTAMP


def validate(data: dict):
    dict_keys = data.keys()
    raise_if_not_exists(keys=dict_keys, key=VAL_SCATTERING)
    raise_if_not_exists(keys=dict_keys, key=VAL_SPECTROMETER)
    raise_if_not_exists(keys=dict_keys, key=VAL_LIFETIME)
    raise_if_not_exists(keys=dict_keys, key=VAL_TIMESTAMP)

    scattering_keys = data[VAL_SCATTERING].keys()
    raise_if_not_exists(keys=scattering_keys, key=VAL_SCATTERING_IMAGE)


def raise_if_not_exists(keys, key: str):
    if key not in keys:
        raise KeyError(f"Key '{key}' does not exists")
