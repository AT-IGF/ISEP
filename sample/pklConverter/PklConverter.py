import gzip
import os
import pickle
import time
from pathlib import Path
from typing import Generator

import numpy as np

from sample.pklConverter.models.RawDataBase import RawDataBase
from sample.pklConverter.processing.Converter import  Converter

def save_data(filepath: str | Path, data: list[RawDataBase]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(filepath, 'wb', compresslevel=4) as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_data(filepath: str | Path) -> list[RawDataBase]:
    with gzip.open(filepath, 'rb') as f:
        return pickle.load(f)

def zip_to_plk_gz(filepath: Path) -> Path:
    return filepath.with_suffix('.pkl.gz')

def iter_files(src: Path) -> Generator[Path, None, None]:
    stack = [src]
    while stack:
        for entry in os.scandir(stack.pop()):
            if entry.is_dir(follow_symlinks=False):
                stack.append(entry.path)
            elif entry.is_file(follow_symlinks=False):
                yield Path(entry.path).relative_to(src)

def main():
    src_input = input("Measurements root path: ")
    dst_input = input("Mapped files output path: ")
    src = Path(src_input)
    dst = Path(dst_input)
    files_chunk = iter_files(src)

    start = time.time()
    for idx, file in enumerate(files_chunk):
        try:
            dst_file_path = dst / file.with_suffix('.pkl.gz')
            if idx %1000==0:
                print(idx)
            if dst_file_path.exists():
                continue
            converter = Converter()
            raw_data: list[RawDataBase] = converter.map_to_raw_data(filename=src / file)
            save_data(dst_file_path, data=raw_data)
        except:
            pass
    elapsed = time.time() - start
    print(f"{elapsed:.2f}s")


if __name__ == "__main__":
    main()