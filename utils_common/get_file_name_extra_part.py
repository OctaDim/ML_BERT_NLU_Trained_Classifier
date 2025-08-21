import os
import random
from datetime import datetime

from configs.settings import BERT_OPTIONS
from utils_common.normalized_path import get_full_file_normal_path


def get_file_name_with_extra_part(orig_file_full_path: str,
                                  filename_prefix: str) -> str:
    directory_full_path = os.path.dirname(orig_file_full_path)
    orig_file_basename = os.path.basename(orig_file_full_path)
    orig_filename, orig_ext = os.path.splitext(orig_file_basename)

    datetime_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
    random_str = str(random.randint(10000, 99999))
    extra_filename_part = f"{filename_prefix}_{datetime_str}-{random_str}"
    file_name_with_extra = f"{orig_filename}_{extra_filename_part}{orig_ext}"

    new_file_full_path = get_full_file_normal_path(
        all_dir_str_parts=[directory_full_path, ],
        file_name_with_ext=file_name_with_extra)
    return new_file_full_path
