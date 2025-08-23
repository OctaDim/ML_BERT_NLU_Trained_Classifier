import os

from configs.settings import BASE_DIR, BERT_OPTIONS
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)


def get_initial_dataset_dir_path():
    bert_dataset_init_dir_path = ""
    init_lab_cat_csv_path = ""
    init_text_lab_csv_path = ""
    try:
        bert_dataset_init_dir_path = get_full_dir_normal_path(
            [BASE_DIR, BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH])

        if not os.path.isdir(bert_dataset_init_dir_path):
            print(f"Dataset initial directory not found [ERROR]:\n"
                  f"bert_dataset_init_dir_path: {bert_dataset_init_dir_path}\n"
                  f"return bert_dataset_init_dir_path = ''")
            bert_dataset_init_dir_path = ""
            return bert_dataset_init_dir_path

        init_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[bert_dataset_init_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

        init_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[bert_dataset_init_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

        csv_files_exist_flag = all([os.path.isfile(init_lab_cat_csv_path),
                                    os.path.isfile(init_text_lab_csv_path)])
        if not csv_files_exist_flag:
            print(f"Dataset initial csv files not found [ERROR]:\n"
                  f"bert_dataset_init_dir_path: {bert_dataset_init_dir_path}\n"
                  f"init_lab_cat_csv_path: {init_lab_cat_csv_path}\n"
                  f"init_text_lab_csv_path: {init_text_lab_csv_path}\n"
                  f"return bert_dataset_init_dir_path = ''")
            bert_dataset_init_dir_path = ""
        return bert_dataset_init_dir_path
    except Exception as error:
        print(f"Read initial dataset dir or files [ERROR]: error: {error}\n"
              f"bert_dataset_init_dir_path: {bert_dataset_init_dir_path}\n"
              f"init_lab_cat_csv_path: {init_lab_cat_csv_path}\n"
              f"init_text_lab_csv_path: {init_text_lab_csv_path}\n")
