import logging

from src.common import Consts


def get_batch_size(batch_size):
    if batch_size is not None:
        return batch_size
    return Consts.BATCH_SIZE_DEFAULT


def get_buffer_size(batch_size):

    if batch_size is not None:
        return batch_size
    default_buffer = Consts.BUFFER_SIZE_DEFAULT
    return default_buffer
