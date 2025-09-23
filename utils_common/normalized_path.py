import os
from typing import Literal


def get_full_file_normal_path(all_dir_str_parts: list[str],
                              file_name_with_ext: str) -> str:
    results_file_path = os.path.join(*all_dir_str_parts, file_name_with_ext)
    normalized_file_path = os.path.normpath(results_file_path)
    return normalized_file_path


def get_full_dir_normal_path(all_dir_str_parts: list[str]
                             ) -> Literal[""] | str | bytes:
    if not all_dir_str_parts:
        normalized_dirs_path = os.path.normpath("")
    else:
        results_file_path = os.path.join(*all_dir_str_parts)
        normalized_dirs_path = os.path.normpath(results_file_path)
    return normalized_dirs_path
