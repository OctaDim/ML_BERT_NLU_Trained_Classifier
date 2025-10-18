import random
from datetime import datetime

from configs.settings import BASE_DIR, BERT_OPTIONS
from utils_common.normalized_path import get_full_dir_normal_path


def get_new_model_random_dir_path() -> str:
    datetime_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
    random_str = str(random.randint(10000, 99999))
    prefix = BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_DIR_PREFIX
    new_model_dir = f"{prefix}_{datetime_str}-{random_str}"

    new_model_base_dir = BERT_OPTIONS.BERT_NEW_DATASETS_CSV_BASE_PATH
    new_dataset_dir_path = get_full_dir_normal_path(
        [BASE_DIR, BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH, new_model_dir])
    return new_model_base_dir
