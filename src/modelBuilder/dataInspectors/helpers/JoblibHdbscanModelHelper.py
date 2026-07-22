import os
import pickle
import joblib
from typing import Union
import logging
import hdbscan
from src.core import PathHelper

logger = logging.getLogger()


def save_hdbscan(model, filepath: str, compress: int = 3) -> None:
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    except FileNotFoundError:
        pass  # Handles cases where directory is current dir

    extension = PathHelper.get_extension(filepath)
    if extension == ".joblib":
        joblib.dump(model, filepath, compress=compress)
    elif extension == ".pickle":
        with open(filepath, "wb") as f:
            pickle.dump(model, f)
    else:
        raise ValueError(f"Unsupported serialization method: {extension}")

    logger.info(f"Model saved to {filepath} using {extension}")


def load_hdbscan(
    filepath: str,
) -> Union[hdbscan.HDBSCAN, None]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No file found at {filepath}")

    extension = PathHelper.get_extension(filepath)

    if extension == ".joblib":
        import joblib

        return joblib.load(filepath)
    elif extension == ".pickle":
        with open(filepath, "rb") as f:
            return pickle.load(f)
    else:
        raise ValueError(f"Unknown load method: {extension}")
