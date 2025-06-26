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
    API_PRODUCT_SERVER_IP = "API_prod_server_255_255_255_255_8000"
    API_TEST_PORT_ANY_IP = "API_port_all_ips_0_0_0_0_8000"
    API_TEST_WIN_LOCALHOST = "API_win_localhost_127_0_0_1_8000"
    API_TEST_UNIX_LOCALHOST = "API_unix_localhost_127_0_1_1_8000"
    API_TEST_DEXP_IP = "API_dexp_ip_192_168_0_117_8000"


full_path = os.path.join(BASE_DIR, ".configs.ini")
normal_env_path = os.path.normpath(full_path)
api_configs = ConfigParser()
api_configs.read(filenames=normal_env_path)

get_cur_internal_ip(log_ip=True)
cur_external_ip = get_cur_external_ip_via_google_dns(log_ip=True)

if cur_external_ip == "255.255.255.255":
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


@dataclass
class BERT_MODEL_NAMES:
    BERT_BASE_MULTILINGUAL_CASED: str = "bert-base-multilingual-cased"


@dataclass
class BERT_OPTIONS:
    BERT_MODEL_INIT: bool = True
    BERT_ACTIVE_MODEL_NAME: str = BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED
    BERT_MODELS_DOWNLOAD_PATH: str = "ML_BERT_classifier/model_bert_init_pretrained"
    BERT_TRAINED_MODELS_SAVE_PATH: str = "ML_BERT_classifier/models_bert_product_trained"
    BERT_TRAINED_MODELS_SAVE_DIR_PREFIX: str = "trained_bert"
    BERT_API_URL_BASE_NAME: str = "bert"


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
    BERT_TRAIN_MAX_EPOCHS_NUMBER: int = 3
    CONTINUOUS_100PERC_EPOCHS: int = 5
    BERT_TRAIN_BATCH_SUZE: int = 8
    BERT_TRAIN_LEARNING_RATE: int = 5e-5
    BERT_TOKEN_STR_MAX_LENGTH: int = 64
    BERT_TOKEN_TRUNCATION: bool = False
    BERT_TOKEN_PADDING: Union[Literal["max_length", "longest"], False, None] = "max_length"
    BERT_RETURN_TENSOR: Union[Literal["pt", "tf", "np"], None] = "pt"
