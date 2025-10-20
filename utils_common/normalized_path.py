import os
from typing import Literal


def get_full_file_normal_path(
        all_dir_str_parts: list[str | Literal[""] | os.PathLike | bytes],
        file_name_with_ext: str) -> str:
    results_file_path = os.path.join(*all_dir_str_parts, file_name_with_ext)
    normalized_file_path = os.path.normpath(results_file_path)
    normalized_file_path_str = str(normalized_file_path)
    return normalized_file_path_str


def get_full_dir_normal_path(
        all_dir_str_parts: list[str | Literal[""] | os.PathLike | bytes]
) -> str:
    if all_dir_str_parts:
        results_file_path = os.path.join(*all_dir_str_parts)
        normalized_dirs_path = os.path.normpath(results_file_path)
    else:
        normalized_dirs_path = os.path.normpath("")
    normalized_dirs_path_str = str(normalized_dirs_path)
    return normalized_dirs_path_str
