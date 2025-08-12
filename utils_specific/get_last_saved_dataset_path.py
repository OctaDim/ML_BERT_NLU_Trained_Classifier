import os

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.settings import BASE_DIR, BERT_OPTIONS
from utils_common.normalized_path import get_full_file_normal_path, get_full_dir_normal_path


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
                dataset_file_saved_path = dataset_ini_file.readline()
                dataset_file_saved_path = dataset_file_saved_path.strip()
        else:
            dataset_file_saved_path = ""
    except Exception as error:
        dataset_file_saved_path = ""  # not necessary, for reliability
        print(f"Read last model saved ini file [ERROR]: error: {error}, "
              f"last_saved_dataset_ini_dir: {last_saved_dataset_ini_dir}, "
              f"last_saved_dataset_ini_path: {last_saved_dataset_ini_path}")

    if bert_model_inst.last_saved_dataset_dir:
        last_saved_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
    elif dataset_file_saved_path:
        last_saved_dataset_dir_path = dataset_file_saved_path
    else:
        initial_dataset_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
        last_saved_dataset_dir_path = get_full_dir_normal_path(
            [BASE_DIR, initial_dataset_dir])
        if not (os.path.exists(last_saved_dataset_dir_path)
                and os.path.isdir(last_saved_dataset_dir_path)):
            last_saved_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
    return last_saved_dataset_dir_path
