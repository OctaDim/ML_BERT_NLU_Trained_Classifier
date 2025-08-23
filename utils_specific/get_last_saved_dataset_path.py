import os

from configs.settings import BASE_DIR, BERT_OPTIONS
from utils_common.normalized_path import get_full_file_normal_path


def get_last_saved_dataset_dir_path() -> str | None:
    last_saved_dataset_ini_dir = ""
    last_saved_dataset_ini_path = ""
    try:
        last_saved_dataset_ini_path = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)

        if os.path.isfile(last_saved_dataset_ini_path):
            with open(file=last_saved_dataset_ini_path,
                      mode="r", encoding="utf-8") as dataset_ini_file:
                dataset_ini_file.seek(0)
                last_saved_dataset_dir_path = dataset_ini_file.readline()
                last_saved_dataset_dir_path = last_saved_dataset_dir_path.strip()
        else:
            last_saved_dataset_dir_path = ""

        if not os.path.isdir(last_saved_dataset_dir_path):
            print(f"Last dataset file saved path not found [ERROR]:\n"
                  f"last_saved_dataset_ini_path: {last_saved_dataset_ini_path}\n"
                  f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n")
            last_saved_dataset_dir_path = ""
            return last_saved_dataset_dir_path

        saved_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[last_saved_dataset_ini_path],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

        saved_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[last_saved_dataset_ini_path],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

        csv_files_exist_flag = all([os.path.isfile(saved_lab_cat_csv_path),
                                    os.path.isfile(saved_text_lab_csv_path)])

        if not csv_files_exist_flag:
            print(f"Dataset saved csv files not found [ERROR]:\n"
                  f"last_saved_dataset_ini_path: {last_saved_dataset_ini_path}\n"
                  f"saved_lab_cat_csv_path: {saved_lab_cat_csv_path}\n"
                  f"saved_text_lab_csv_path: {saved_text_lab_csv_path}\n"
                  f"return last_saved_dataset_dir_path = ''")
            last_saved_dataset_dir_path = ""
        return last_saved_dataset_dir_path
    except Exception as error:
        print(f"Read last saved dataset ini file [ERROR]: error: {error}, "
              f"last_saved_dataset_ini_dir: {last_saved_dataset_ini_dir}, "
              f"last_saved_dataset_ini_path: {last_saved_dataset_ini_path}")
