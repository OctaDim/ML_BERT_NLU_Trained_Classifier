import os
import sys
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Union

from dotenv import load_dotenv

from utils_common.get_cur_ip_address import (
    get_cur_external_ip_via_google_dns, get_cur_internal_ip)

BASE_DIR = Path(__file__).resolve().parent.parent

full_path = os.path.join(BASE_DIR, ".env")
normal_env_path = os.path.normpath(full_path)
env = load_dotenv(normal_env_path)  # for future
API_TEST_USERNAME = os.getenv("API_TEST_USERNAME")
API_TEST_PASSWORD = os.getenv("API_TEST_PASSWORD")


@dataclass
class API_CONFIG_NAMES:
    API_PRODUCT_SERVER_IP = "production"
    API_HAKASIA_PROD_SERVER_IP = "API_Hakasia_product_server"
    API_TEST_176_124_136_22_IP = "API_prod_server_176_124_136_22_8000"
    API_TEST_PORT_ANY_IP = "API_port_all_ips_0_0_0_0_8000"
    API_TEST_WIN_LOCALHOST = "API_win_localhost_127_0_0_1_8000"
    API_TEST_UNIX_LOCALHOST = "API_unix_localhost_127_0_1_1_8000"
    API_TEST_DEXP_IP = "API_dexp_ip_192_168_0_117_8000"


full_path = os.path.join(BASE_DIR, ".configs_api.ini")
normal_env_path = os.path.normpath(full_path)
api_configs = ConfigParser()
api_configs.read(filenames=normal_env_path)

get_cur_internal_ip(log_ip=True)
cur_external_ip = get_cur_external_ip_via_google_dns(log_ip=True)

if cur_external_ip == "___.___.___.___":  # Just example
    api_conf_name = API_CONFIG_NAMES.API_TEST_PORT_ANY_IP
elif cur_external_ip == "172.19.201.24":
    api_conf_name = API_CONFIG_NAMES.API_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    api_conf_name = API_CONFIG_NAMES.API_HAKASIA_PROD_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    api_conf_name = API_CONFIG_NAMES.API_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.0.117":
    api_conf_name = API_CONFIG_NAMES.API_TEST_DEXP_IP
elif sys.platform == "linux":
    api_conf_name = API_CONFIG_NAMES.API_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    api_conf_name = API_CONFIG_NAMES.API_TEST_WIN_LOCALHOST
else:
    api_conf_name = API_CONFIG_NAMES.API_TEST_PORT_ANY_IP

API_HOST: str = api_configs.get(section=api_conf_name, option="API_HOST")
API_PORT: int = int(api_configs.get(section=api_conf_name, option="API_PORT"))
API_USERNAME: str = api_configs.get(section=api_conf_name, option="API_USERNAME")
API_PASSWORD: str = api_configs.get(section=api_conf_name, option="API_PASSWORD")


class DB_CONFIG_NAMES:
    REDIS_PRODUCT_ANY_IP = "Redis_any_ip_prod_configs"


if cur_external_ip == "___.___.___.___":
    redis_conf_name = DB_CONFIG_NAMES.REDIS_PRODUCT_ANY_IP  # Certain configs can be defined
else:
    redis_conf_name = DB_CONFIG_NAMES.REDIS_PRODUCT_ANY_IP

full_path = os.path.join(BASE_DIR, ".configs_redis.ini")
normal_env_path = os.path.normpath(full_path)
db_configs = ConfigParser()
db_configs.read(filenames=normal_env_path)

REDIS_HOST = db_configs.get(section=redis_conf_name, option="REDIS_HOST")
REDIS_PORT = db_configs.get(section=redis_conf_name, option="REDIS_PORT")
REDIS_DB = db_configs.get(section=redis_conf_name, option="REDIS_DATABASE")
REDIS_PASSWORD = db_configs.get(section=redis_conf_name, option="REDIS_PASSWORD") or None


@dataclass
class REDIS_OPTIONS:
    DECODE_RESPONSES = True
    SOCKET_CONNECTION_TIMEOUT = 5
    SOCKET_KEEPALIVE = True
    STATUSES_EXPIRY_DAYS = 90
    CHECKSET_TESTS_EXPIRY_DAYS = 90


@dataclass
class BERT_MODEL_NAMES:
    BERT_BASE_MULTILINGUAL_CASED: str = "bert-base-multilingual-cased"


@dataclass
class BERT_OPTIONS:
    # API
    BERT_API_URL_BASE_NAME: str = "bert"
    # INITIAL MODEL PATH OPTIONS
    BERT_MODEL_INIT: bool = True
    BERT_ACTIVE_MODEL_NAME: str = BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED
    BERT_INITIAL_MODEL_DOWNLOAD_PATH: str = "ML_BERT_models/model_bert_init_pretrained"
    # TRAINED MODELS BASE PATH OPTIONS
    BERT_TRAINED_MODELS_BASE_PATH: str = "WORKING_DATA/trained_product_bert_models"
    BERT_TRAINED_MODELS_SAVE_DIR_PREFIX: str = "trained_bert"
    # DATASETS CSV OPTIONS
    BERT_INITIAL_DATASET_CSV_PATH: str = "ML_BERT_train_datasets/product_init_train_dataset"
    BERT_TRAIN_DATASET_FILE_EXTENSIONS: tuple = ("xlsx", "xls", "txt", "csv")
    BERT_NEW_DATASETS_CSV_BASE_PATH: str = "WORKING_DATA/updated_product_train_datasets"
    BERT_LABEL_CATEGORY_CSV_FILE_NAME: str = "prod_labels_categories.csv"
    BERT_TEXT_LABEL_CSV_FILE_NAME: str = "prod_texts_labels.csv"
    BERT_OVERWRITE_PREV_CSV_DATASET: bool = False
    BERT_NEW_DATASET_CSV_DIR_PREFIX: str = "updated_dataset"
    # MODEL AND CSV SAVE PATHS INI FILES OPTIONS
    BERT_LAST_SAVED_MODEL_INI_FILE_PATH: str = "WORKING_DATA/last_saved_model_ini_file/last_saved_model_dir_path.ini"
    BERT_LAST_SAVED_DATASET_INI_FILE_PATH: str = "WORKING_DATA/last_saved_dataset_ini_file/last_saved_dataset_dir_path.ini"
    BERT_BEFORE_REINIT_MODEL_TEMP_PATH: str = "WORKING_DATA/temp_saved_model_prior_init_train"
    # CHECKSETS OPTIONS
    BERT_CHECKSET_NAME_REDIS_PREFIX: str = "test_checkset"
    BERT_CONFUSION_MATRICES_IMAGES_PATH: str = "WORKING_DATA/confusion_matrices_images"
    BERT_CONFUSION_MATRIX_AXE_TITLE: str = "Confusion Matrix"
    BERT_CONFUSION_MATRIX_TRUE_LABEL_TXT: str = "True Labels - Правильные Классы"
    BERT_CONFUSION_MATRIX_PREDICT_LABEL_TXT: str = "Predicted Labels - Предсказанные Классы"
    # LEARNING FILES OPTIONS
    BERT_UNIQUE_LEARNING_FILE_PREFIX: str = "unique"
    BERT_UNIQUE_LEARNING_FILES_PATH: str = "WORKING_DATA/learn_files_unique"


@dataclass
class BERT_TRAIN_OPTIONS:
    """BERT_TOKEN_PADDING note
    str: "max_length" - add symbols till BERT_TOKEN_STR_MAX_LENGTH
    str: "longest" - add symbols till the longest text in the batch
    False/None - padding is not used
    BERT_RETURN_TENSOR note:
    str: "pt" - returns PyTorch tensors (Necessary for this project)
    str: "tf" - returns TensorFlow tensors
    str: "np" - returns NumPy arrays
    None - returns lists"""
    BERT_TRAIN_MAX_EPOCHS_NUMBER: int = 50
    CONTINUOUS_100PERC_EPOCHS: int = 5
    BERT_TRAIN_BATCH_SUZE: int = 8
    BERT_TRAIN_LEARNING_RATE: int = 5e-5
    BERT_TOKEN_STR_MAX_LENGTH: int = 64
    BERT_TOKEN_TRUNCATION: bool = False
    BERT_TOKEN_PADDING: Union[Literal["max_length", "longest"], False, None] = "max_length"
    BERT_RETURN_TENSOR: Union[Literal["pt", "tf", "np"], None] = "pt"


@dataclass
class STATUSES:
    STATUS_DATASET_CREATION_START_EN = "Preparing dataset tarted"
    STATUS_DATASET_CREATION_FINISH_EN = "Preparing dataset tarted"

    STATUS_MODEL_REINIT_START_EN = "Model reinitialising before training started"
    STATUS_MODEL_REINIT_FINISH_EN = "Model reinitialising before training finished"

    STATUS_MODEL_TRAIN_PENDING_EN = "Training model pending"
    STATUS_MODEL_TRAIN_START_EN = "Model training started"
    STATUS_MODEL_TRAIN_PROCESS_EN = "Model training in process"
    STATUS_MODEL_TRAIN_FINISH_EN = "Model training without saving finished"
    STATUS_TRAIN_WITHOUT_SAVE_COMPLETE_EN = "Model training without saving completed"

    STATUS_TRAINED_MODEL_SAVE_START_EN = "Trained model saving started"
    STATUS_TRAINED_MODEL_SAVE_PROCESS_EN = "Trained model saving in process"
    STATUS_TRAINED_MODEL_SAVE_FINISH_EN = "Trained model saving finished"
    STATUS_TRAIN_AND_SAVE_COMPLETE_EN = "Model training and saving completed"

    STATUS_CHECKSET_TEST_PENDING_EN = "Check-set model test pending"
    STATUS_CHECKSET_TEST_START_EN = "Check-set model test started"
    STATUS_CHECKSET_TEST_PROCESS_EN = "Check-set model test in process"
    STATUS_CHECKSET_TEST_FINISH_EN = "Check-set model test finished"
