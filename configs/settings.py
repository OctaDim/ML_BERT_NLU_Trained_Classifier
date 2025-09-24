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

# GETTING TEST ENV CONFIGS #############################################
test_env_full_path = os.path.join(BASE_DIR, ".env")
test_env_normal_path = os.path.normpath(test_env_full_path)
env = load_dotenv(test_env_normal_path)  # for future
API_TEST_USERNAME = os.getenv("API_TEST_USERNAME")
API_TEST_PASSWORD = os.getenv("API_TEST_PASSWORD")

# GETTING CURENT INTERNAL AND EXTERNAL IPs #############################
get_cur_internal_ip(log_ip=True)
cur_external_ip = get_cur_external_ip_via_google_dns(log_ip=True)


# GETTING API INI CONFIGS ##############################################
@dataclass(frozen=True)
class API_CONFIG_NAMES:
    API_PRODUCT_SERVER_IP = "API_production"
    API_HAKASIA_PROD_SERVER_IP = "API_Hakasia_product_server"
    API_TEST_176_124_136_22_IP = "API_prod_server_176_124_136_22_8000"
    API_TEST_PORT_ANY_IP = "API_port_all_ips_0_0_0_0_8000"
    API_TEST_WIN_LOCALHOST = "API_win_localhost_127_0_0_1_8000"
    API_TEST_UNIX_LOCALHOST = "API_unix_localhost_127_0_1_1_8000"
    API_TEST_DEXP_IP = "API_dexp_ip_192_168_0_117_8000"


api_ini_full_path = os.path.join(BASE_DIR, ".configs_api.ini")
api_ini_normal_path = os.path.normpath(api_ini_full_path)
api_conf_parser = ConfigParser()
api_conf_parser.read(filenames=api_ini_normal_path)

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

API_HOST: str = api_conf_parser.get(section=api_conf_name, option="API_HOST")
API_PORT: int = int(api_conf_parser.get(section=api_conf_name, option="API_PORT"))
API_USERNAME: str = api_conf_parser.get(section=api_conf_name, option="API_USERNAME")
API_PASSWORD: str = api_conf_parser.get(section=api_conf_name, option="API_PASSWORD")


# GETTING REDIS INI CONFIGS ############################################
@dataclass(frozen=True)
class REDIS_CONFIG_NAMES:
    REDIS_PRODUCT_ANY_IP = "Redis_any_ip_prod_configs"


redis_ini_full_path = os.path.join(BASE_DIR, ".configs_redis.ini")
redis_ini_normal_path = os.path.normpath(redis_ini_full_path)
redis_conf_parser = ConfigParser()
redis_conf_parser.read(filenames=redis_ini_normal_path)

if cur_external_ip == "___.___.___.___":
    redis_conf_name = REDIS_CONFIG_NAMES.REDIS_PRODUCT_ANY_IP  # Certain configs can be defined
else:
    redis_conf_name = REDIS_CONFIG_NAMES.REDIS_PRODUCT_ANY_IP

REDIS_HOST = redis_conf_parser.get(section=redis_conf_name, option="REDIS_HOST")
REDIS_PORT = redis_conf_parser.get(section=redis_conf_name, option="REDIS_PORT")
REDIS_DB = redis_conf_parser.get(section=redis_conf_name, option="REDIS_DATABASE")
REDIS_PASSWORD = redis_conf_parser.get(section=redis_conf_name, option="REDIS_PASSWORD") or None


# GETTING POSTGRES INI CONFIGS #########################################
@dataclass(frozen=True)
class POSTGRES_CONFIG_NAMES:
    POSTGRES_PRODUCT_SERVER_IP = "Postgres_production"
    POSTGRES_HAKASIA_PROD_SERVER_IP = "Postgres_Hakasia_product_server"
    POSTGRES_TEST_176_124_136_22_IP = "Postgres_prod_server_176_124_136_22"
    POSTGRES_TEST_PORT_ANY_IP = "Postgres_port_all_ips_0_0_0_0_8000"
    POSTGRES_TEST_WIN_LOCALHOST = "Postgres_win_localhost_127_0_0_1_8000"
    POSTGRES_TEST_UNIX_LOCALHOST = "Postgres_unix_localhost_127_0_1_1_8000"
    POSTGRES_TEST_DEXP_IP = "Postgres_dexp_ip_192_168_0_117_8000"


postgres_ini_full_path = os.path.join(BASE_DIR, ".configs_postgres.ini")
postgres_ini_normal_path = os.path.normpath(postgres_ini_full_path)
postgres_conf_parser = ConfigParser()
postgres_conf_parser.read(filenames=postgres_ini_normal_path)

if cur_external_ip == "___.___.___.___":  # Just example
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_PORT_ANY_IP
elif cur_external_ip == "172.19.201.24":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_PRODUCT_SERVER_IP
elif cur_external_ip == "172.19.201.24":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_HAKASIA_PROD_SERVER_IP
elif cur_external_ip == "176.124.136.22":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_176_124_136_22_IP
elif cur_external_ip == "192.168.0.117":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_DEXP_IP
elif sys.platform == "linux":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_UNIX_LOCALHOST
elif sys.platform == "win32":
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_WIN_LOCALHOST
else:
    postgres_conf_name = POSTGRES_CONFIG_NAMES.POSTGRES_TEST_PORT_ANY_IP

POSTGRES_USER = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_USER")
POSTGRES_PASSWORD = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_PASSWORD")
POSTGRES_HOST = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_HOST")
POSTGRES_PORT = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_PORT") or None
POSTGRES_DB_NAME = postgres_conf_parser.get(section=postgres_conf_name, option="POSTGRES_DB_NAME")


@dataclass(frozen=True)
class FASTAPI_OPTIONS:
    LOG_LEVEL = "debug"
    USE_COLORS = True


@dataclass(frozen=True)
class ALCHEMY_OPTIONS:
    USE_POSTGRES_DATA_BASE: bool = True
    ALCHEMY_ORM_RAW_SQL_CONSOLE_LOGS: bool = False
    ALCHEMY_QUERY_EXEC_TIME_LOGS: bool = False
    ALCHEMY_SESSION_OK_ACTIONS_LOGS: bool = False
    ALCHEMY_USE_FUTURE_ALCHEMY: bool = True
    ALCHEMY_POOL_PRE_PING: bool = True
    ALCHEMY_CONST_CONN_POOL_SIZE: int = 20
    ALCHEMY_TEMP_CONN_MAX_OVERFLOW: int = 30
    ALCHEMY_POOL_RECYCLE: int = 600  # seconds
    ALCHEMY_POOL_TIMEOUT: int = 30  # seconds


@dataclass(frozen=True)
class REDIS_OPTIONS:
    DECODE_RESPONSES = True
    SOCKET_CONNECTION_TIMEOUT = 5
    SOCKET_KEEPALIVE = True
    STATUSES_EXPIRY_DAYS = 90
    CHECKSET_TESTS_EXPIRY_DAYS = 90


@dataclass(frozen=True)
class BERT_MODEL_NAMES:
    BERT_BASE_MULTILINGUAL_CASED: str = "bert-base-multilingual-cased"


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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


@dataclass(frozen=True)
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
