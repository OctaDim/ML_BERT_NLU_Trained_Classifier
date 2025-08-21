# import asyncio
# from functools import partial
import os
from datetime import timedelta

from fastapi import APIRouter

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.settings import (
    BERT_OPTIONS, BASE_DIR)
from db_redis.init_redis import RedisAsyncConnection
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_common.normalized_path import get_full_dir_normal_path, get_full_file_normal_path

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_develop_test_endpoint = APIRouter(prefix=f"/{bert_base_url_name}",
                                         tags=["DEVELOP TEST ENDPOINT"])


@router_develop_test_endpoint.post(path="/develop_test_endpoint/",
                                   response_model=None)
async def develop_test_endpoint(auth_data: AuthDataBert):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ TEST ENDPOINT [START]")
    # async with RedisAsyncConnection() as redis_conn:
    #     await redis_conn.setex("TestKey", timedelta(minutes=10), "TestValue")
    #
    # async with RedisAsyncConnection() as redis_conn:
    #     key_value = await redis_conn.get("TestKey")
    #     print("############################# key_value", key_value)

    # last_saved_dataset_ini_dir = ""
    # last_saved_dataset_ini_path = ""
    #
    # try:
    #     last_saved_dataset_ini_path = get_full_file_normal_path(
    #         all_dir_str_parts=[BASE_DIR],
    #         file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)
    #
    #     if os.path.isfile(last_saved_dataset_ini_path):
    #         with open(file=last_saved_dataset_ini_path,
    #                   mode="r", encoding="utf-8") as dataset_ini_file:
    #             dataset_ini_file.seek(0)
    #             dataset_file_saved_path = dataset_ini_file.read()
    #     else:
    #         dataset_file_saved_path = ""
    # except Exception as error:
    #     dataset_file_saved_path = ""  # not necessary, for reliability
    #     print(f"Read last model saved ini file [ERROR]: error: {error}, "
    #           f"last_saved_dataset_ini_dir: {last_saved_dataset_ini_dir}, "
    #           f"last_saved_dataset_ini_path: {last_saved_dataset_ini_path}")
    #
    # if bert_model_inst.last_saved_dataset_dir:
    #     train_dataset_dir = bert_model_inst.last_saved_dataset_dir
    # elif dataset_file_saved_path:
    #     train_dataset_dir = dataset_file_saved_path
    # else:
    #     initial_dataset_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
    #     train_dataset_dir = get_full_dir_normal_path(
    #         [BASE_DIR, initial_dataset_dir])
    #     if not (os.path.exists(train_dataset_dir)
    #             and os.path.isdir(train_dataset_dir)):
    #         train_dataset_dir = bert_model_inst.last_saved_dataset_dir
    #
    # all_dataset_dirs = train_dataset_dir.split(os.sep)
    # dataset_container_dir = all_dataset_dirs[-1]
    # print("############ train_dataset_dir", train_dataset_dir)
    # print("############ dataset_container_dir", dataset_container_dir)
    print(f"******* bert_model_inst: {bert_model_inst}\n")
    print(f"******* hash(bert_model_inst): {hash(bert_model_inst)}\n")
    print(f"******* bert_model_inst.model: {bert_model_inst.model}\n")
    print(f"******* hash(bert_model_inst.model): {hash(bert_model_inst.model)}\n")
    print(f"####### bert_model_inst.model.config.num_labels: {bert_model_inst.model.config.num_labels}")
    print(f"####### bert_model_inst.model.config.num_labels: {bert_model_inst.model.config.num_labels}")
    print(f"####### bert_model_inst.model.config.id2label: {bert_model_inst.model.config.id2label}")
    print(f"####### bert_model_inst.model.config.label2id: {bert_model_inst.model.config.label2id}")
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ TEST ENDPOINT [FINISH]")
