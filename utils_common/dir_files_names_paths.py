import os

from utils_common.normalized_path import get_full_file_normal_path


def get_dir_files_only_names(full_dir_path):
    dir_files_only_names = []
    for cur_entry_only_name in os.listdir(full_dir_path):  # files and dirs only str names
        full_file_path = get_full_file_normal_path(
            all_dir_str_parts=[full_dir_path],
            file_name_with_ext=cur_entry_only_name)
        if os.path.isfile(full_file_path):
            dir_files_only_names.append(cur_entry_only_name)

    if not dir_files_only_names:
        print(f"No files in defined directory [ERROR]: "
              f"full_dir_path: {full_dir_path}, "
              f"dir_files_only_names: {dir_files_only_names}\n")
    return dir_files_only_names


def get_dir_files_full_paths(full_dir_path):
    dir_files_full_paths = []
    for cur_entry_obj in os.scandir(full_dir_path):  # files and dirs objs, not str names
        if cur_entry_obj.is_file():
            dir_files_full_paths.append(cur_entry_obj.path)

    if not dir_files_full_paths:
        print(f"No files in defined directory [ERROR]: "
              f"full_dir_path: {full_dir_path}, "
              f"dir_files_full_paths: {dir_files_full_paths}\n")
    return dir_files_full_paths
