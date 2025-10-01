import os

from configs.settings import BASE_DIR, BERT_OPTIONS
from utils_common.normalized_path import get_full_file_normal_path


def get_last_saved_model_dir_path() -> str | None:
    last_saved_model_ini_fpath = ""
    last_saved_model_dir_path = ""
    try:
        last_saved_model_ini_fpath = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_MODEL_INI_FILE_PATH)
        if not os.path.isfile(last_saved_model_ini_fpath):
            print(f"Last saved model ini file not found [ERROR]:\n"
                  f"last_saved_model_ini_fpath: {last_saved_model_ini_fpath}\n"
                  f"last_saved_model_dir_path: {last_saved_model_dir_path}\n")
            return last_saved_model_dir_path

        with open(file=last_saved_model_ini_fpath,
                  mode="r", encoding="utf-8") as model_ini_file:
            model_ini_file.seek(0)
            last_saved_model_dir_path = model_ini_file.readline().strip()

        if not os.path.isdir(last_saved_model_dir_path):
            print(f"Last saved model dir path not found [ERROR]:\n"
                  f"last_saved_model_ini_fpath: {last_saved_model_ini_fpath}\n"
                  f"last_saved_model_dir_path: {last_saved_model_dir_path}\n")
            last_saved_model_dir_path = ""
        return last_saved_model_dir_path
    except Exception as error:
        print(f"Read last saved model ini file or dir path [ERROR]: "
              f"error: {error}\n"
              f"last_saved_model_ini_fpath: {last_saved_model_ini_fpath}\n"
              f"last_saved_model_dir_path: {last_saved_model_dir_path}\n")
