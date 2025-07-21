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
    API_PRODUCT_SERVER_IP = "API_prod_server_176_124_136_22_8000"
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

if cur_external_ip == "176.124.136.22":
    api_conf_name = API_CONFIG_NAMES.API_PRODUCT_SERVER_IP
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

full_path = os.path.join(BASE_DIR, ".configs_db.ini")
normal_env_path = os.path.normpath(full_path)
db_configs = ConfigParser()
db_configs.read(filenames=normal_env_path)

REDIS_DATABASE = db_configs.get(section=redis_conf_name, option="REDIS_DATABASE")
REDIS_HOST = db_configs.get(section=redis_conf_name, option="REDIS_HOST")
REDIS_PORT = db_configs.get(section=redis_conf_name, option="REDIS_PORT")
REDIS_PASSWORD = db_configs.get(section=redis_conf_name, option="REDIS_PASSWORD")


@dataclass
class REDIS_OPTIONS:
    DECODE_RESPONSES = True
    SOCKET_CONNECTION_TIMEOUT = 5
    SOCKET_KEEPALIVE = True


@dataclass
class BERT_MODEL_NAMES:
    BERT_BASE_MULTILINGUAL_CASED: str = "bert-base-multilingual-cased"


@dataclass
class BERT_OPTIONS:
    # API
    BERT_API_URL_BASE_NAME: str = "bert"
    # INITIAL MODEL PATH
    BERT_MODEL_INIT: bool = True
    BERT_ACTIVE_MODEL_NAME: str = BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED
    BERT_INITIAL_MODEL_DOWNLOAD_PATH: str = "ML_BERT_models/model_bert_init_pretrained"
    # TRAINED MODELS BASE PATH
    BERT_TRAINED_MODELS_BASE_PATH: str = "WORKING_DATA/trained_product_bert_models"
    BERT_TRAINED_MODELS_SAVE_DIR_PREFIX: str = "trained_bert"
    # DATASETS CSV
    BERT_INITIAL_DATASET_CSV_PATH: str = "ML_BERT_train_datasets/product_init_train_dataset"
    BERT_TRAIN_DATASET_FILE_EXTENSIONS: tuple = ("xlsx", "xls", "txt", "csv")
    BERT_NEW_DATASETS_CSV_BASE_PATH: str = "WORKING_DATA/updated_product_train_datasets"
    BERT_LABEL_CATEGORY_CSV_FILE_NAME: str = "prod_labels_categories.csv"
    BERT_TEXT_LABEL_CSV_FILE_NAME: str = "prod_texts_labels.csv"
    BERT_OVERWRITE_PREV_CSV_DATASET: bool = False
    BERT_NEW_DATASET_CSV_DIR_PREFIX: str = "updated_dataset"
    # MODEL AND CSV SAVE PATHS INI FILES
    BERT_LAST_SAVED_MODEL_INI_FILE_PATH: str = "WORKING_DATA/last_saved_model_ini_file/last_saved_model_dir_path.ini"
    BERT_LAST_SAVED_DATASET_INI_FILE_PATH: str = "WORKING_DATA/last_saved_dataset_ini_file/last_saved_dataset_dir_path.ini"


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
