import os

from configs.settings import BASE_DIR, BERT_OPTIONS
from utils_common.normalized_path import get_full_dir_normal_path


def get_initial_model_dir_path():
    bert_model_initial_dir_path = ""
    try:
        bert_model_initial_dir_path = get_full_dir_normal_path(
            [BASE_DIR, BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH])

        if not os.path.isdir(bert_model_initial_dir_path):
            print(f"Model initial dir path not found [ERROR]:\n"
                  f"bert_model_initial_dir_path: {bert_model_initial_dir_path}\n")
            bert_model_initial_dir_path = ""
        return bert_model_initial_dir_path
    except Exception as error:
        print(f"Read model initial dir path [ERROR]: error: {error}\n"
              f"bert_model_initial_dir_path: {bert_model_initial_dir_path}\n")
