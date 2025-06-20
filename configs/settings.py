import os
import sys
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from utils_common.get_cur_ip_address import (
    get_cur_external_ip_via_google_dns, get_cur_internal_ip)


BASE_DIR = Path(__file__).resolve().parent.parent

full_path = os.path.join(BASE_DIR, ".env")
normal_env_path = os.path.normpath(full_path)
env = load_dotenv(normal_env_path)  # for future


# API_HOST: str = os.getenv("API_HOST")
# API_PORT: int = int(os.getenv("API_PORT"))
# API_USERNAME = os.getenv("API_USERNAME")
# API_PASSWORD = os.getenv("API_PASSWORD")

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
    BERT_MODELS_DOWNLOAD_PATH: str = "ML_BERT/models_bert"
    BERT_TRAIN_EPOCHS_NUMBER: int = 50
    BERT_TRAIN_BATCH_SUZE: int = 8
    BERT_TRAIN_LEARNING_RATE: int = 5e-5
