import os


def get_full_file_normal_path(all_dir_str_parts: list[str],
                              file_name_with_ext: str) -> str:
    results_wav_path = os.path.join(*all_dir_str_parts, file_name_with_ext)
    normalized_file_path = os.path.normpath(results_wav_path)
    return normalized_file_path


def get_full_dir_normal_path(all_dir_str_parts: list[str]) -> str:
    results_wav_path = os.path.join(*all_dir_str_parts)
    normalized_dirs_path = os.path.normpath(results_wav_path)
    return normalized_dirs_path
