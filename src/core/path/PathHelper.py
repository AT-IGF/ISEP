#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

import glob
import os
from pathlib import Path

from src.core.files.models.File import File
from src.core.files.models.Files import Files
from src.core.parsers.stringParsers import is_blank


class PathHelper:
    @staticmethod
    def join_absoulte_with_rel_path(dir, rel_path):
        return os.path.realpath(os.path.join(os.path.normpath(dir + rel_path)))

    @staticmethod
    def join_rel_path(dir, rel_path:str, filename=""):
        if rel_path is not None and rel_path.startswith("/mnt"):
            return rel_path
        
        if filename.count("/"):
            raise ValueError(f"Filename='{filename}' contains multiple '/' characters")

        _filename = filename.replace("/", "")
        _rel_path = rel_path
        if _rel_path and _rel_path[-1] == "/":
            _rel_path = _rel_path[:-1]
        if rel_path and _rel_path[0] == "/":
            _rel_path = _rel_path[1:]

        return os.path.realpath(
            os.path.join(
                os.path.normpath(dir), os.path.normpath(f"{_rel_path}/{_filename}")
            )
        )

    @staticmethod
    def join_path(dir, path):
        return os.path.join(os.path.normpath(dir), os.path.normpath((path)))

    @staticmethod
    def is_rel_path(path: str):
        return not os.path.isabs(path)

    @staticmethod
    def get_path(file, rel_path_escapes, path):
        if PathHelper.is_rel_path(path):
            file_dir = os.path.dirname(os.path.realpath(file))
            path = PathHelper.join_rel_path(file_dir, rel_path_escapes + path)

        return path

    @staticmethod
    def get_all_files_by_file_name_part(path, filename_part, extension) -> Files:
        unzip_extension = PathHelper.normalize_extension(extension)
        paths = glob.glob(
            str.format("%s/*%s*%s" % (path, filename_part, unzip_extension))
        )
        files: Files = Files()
        for path in paths:
            files.append_whole_file_path(path)

        return files

    @staticmethod
    def get_all_files(path, extension) -> Files:
        unzip_extension = PathHelper.normalize_extension(extension)
        paths = glob.glob(path + "/*" + unzip_extension)
        files: Files = Files()
        for path in paths:
            files.append_whole_file_path(path)

        return files

    @staticmethod
    def normalize_extension(file_extension):
        if is_blank(file_extension):
            raise ValueError("file_extension cannot be blank")

        if "." in file_extension:
            return file_extension

        return "." + file_extension

    @staticmethod
    def append_text_to_filename(filename: str, text: str):
        f_extension = Path(filename).suffix

        if not f_extension:
            return filename + text

        return filename[: -len(f_extension)] + text + f_extension

    @staticmethod
    def get_file_with_extension(filename: str, extension=".txt"):
        if is_blank(filename):
            raise ValueError("filename cannot be blank")

        extension = PathHelper.normalize_extension(extension)
        f_extension = Path(filename).suffix

        if not f_extension:
            filename = filename + extension

        return filename

    @staticmethod
    def set_path_extension(path, extension: str):
        path = Path(path)
        extension = PathHelper.normalize_extension(extension)
        if path.suffix == extension:
            return path

        return str(path) + extension

    @staticmethod
    def get_extension(filename: str):
        return Path(filename).suffix

    @staticmethod
    def get_filename(filename: str):
        """'filename.txt' -> 'filename'"""
        return Path(filename).stem

    @staticmethod
    def is_file_exists(file_path: str):
        if file_path == None:
            return False
        return os.path.exists(file_path)

    @staticmethod
    def is_file(path: str):
        if path is None:
            return False
        return os.path.isfile(path)

    @staticmethod
    def is_dir_exists(path: str):
        return os.path.isdir(path)

    @staticmethod
    def is_exists(path):
        return PathHelper.is_file_exists(path) or PathHelper.is_dir_exists(path)

    @staticmethod
    def get_dirs(file_path: str):
        return os.path.dirname(file_path)

    @staticmethod
    def get_base_name(file_path: str):
        return os.path.basename(file_path)

    @staticmethod
    def get_files_with_not_existing_path(files: list[File]):
        not_existing_paths = []
        for f in files:
            file_path = f.get_file_path()
            if not PathHelper.is_file_exists(file_path):
                not_existing_paths.append(file_path)

        return not_existing_paths

    @staticmethod
    def get_file_from_full_path(full_path: str):
        head, tail = os.path.split(full_path)
        return File(filename=tail, path=head)

    @staticmethod
    def get_file_from_path_parts(dir: str, rel_path: str, filename=""):
        full_path = PathHelper.join_rel_path(dir, rel_path, filename)
        return PathHelper.get_file_from_full_path(full_path)

    @staticmethod
    def get_absolute_path(base_path, path, raise_on_not_found=True, raise_message=None):
        if path is None:
            raise ValueError(
                "Path cannot be None" if raise_message is None else raise_message
            )

        if base_path is None:
            abs_path = path
        elif str(path).startswith(base_path):
            abs_path = path
        else:
            abs_path = PathHelper.join_rel_path(base_path, path)

        if not PathHelper.is_exists(abs_path) and raise_on_not_found:
            raise FileNotFoundError(
                f"File or directory does not exists under specified path, path={abs_path}"
            )

        return abs_path

    @staticmethod
    def remove_path_base(base_path, path):
        return str(path).replace(base_path, "", 1)

    @staticmethod
    def has_extension(path):
        f_extension = Path(path).suffix
        return not is_blank(f_extension)

    @staticmethod
    def make_dirs(path):
        base = path
        if PathHelper.has_extension(path):
            base = PathHelper.get_dirs(path)
        os.makedirs(base, exist_ok=True)

    @staticmethod
    def get_subdirs(dirs):
        paths_list = []
        for dir in dirs:
            paths_list += glob(f"{dir}/*", recursive=True)
        return paths_list
