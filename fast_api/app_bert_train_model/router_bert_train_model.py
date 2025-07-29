# import asyncio
# from functools import partial
import os
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, status, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_OPTIONS, BASE_DIR, BERT_TRAIN_OPTIONS, BERT_MODEL_NAMES,
    REDIS_OPTIONS)
from db_redis.func_redis_save_key_mapping import redis_save_key_mapping_dict
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_train_model.func_train_save_model_background import (
    background_train_save_model)
from fast_api.app_bert_train_model.scheme_bert_train_model import (
    TrainModelDataBert)
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)
from utils_specific.class_csv_texts_labels import CsvTextLabel

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_train_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                    tags=["BERT"])


@router_bert_train_model.post(path="/bert_train_model/",
                              # TODO: Describe responses here
                              response_model=None)
async def bert_train_model(
        auth_data: AuthDataBert,
        train_model_data: TrainModelDataBert,
        background_tasks: BackgroundTasks  # FastAPI Class for background tasks
):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)

    print("\nGetting last saved dataset full path:")
    # TODO: move to the separate function getting last saved dataset full path
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
                dataset_file_saved_path = dataset_ini_file.read()
        else:
            dataset_file_saved_path = ""
    except Exception as error:
        dataset_file_saved_path = ""  # not necessary, for reliability
        print(f"Read last model saved ini file [ERROR]: error: {error}, "
              f"last_saved_dataset_ini_dir: {last_saved_dataset_ini_dir}, "
              f"last_saved_dataset_ini_path: {last_saved_dataset_ini_path}")

    if bert_model_inst.last_saved_dataset_dir:
        train_dataset_dir = bert_model_inst.last_saved_dataset_dir
    elif dataset_file_saved_path:
        train_dataset_dir = dataset_file_saved_path
    else:
        initial_dataset_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
        train_dataset_dir = get_full_dir_normal_path(
            [BASE_DIR, initial_dataset_dir])
        if not (os.path.exists(train_dataset_dir)
                and os.path.isdir(train_dataset_dir)):
            train_dataset_dir = bert_model_inst.last_saved_dataset_dir

    dataset_path_dirs = train_dataset_dir.split(os.sep)
    dataset_name = dataset_path_dirs[-1]  # As dataset files directory name
    train_task_uuid = str(uuid.uuid4())
    redis_update = {
        "status": REDIS_OPTIONS.STATUS_PENDING,
        "train_task_uuid": train_task_uuid,
        "dataset_name": dataset_name,
        "step_1_pending": "[OK]",
    }
    redis_error = await redis_save_key_mapping_dict(
        key_name=dataset_name,
        mapping_dict=redis_update,
        expiry_seconds=REDIS_KEY_EXPIRE_TIME)
    if redis_error:
        print(redis_error)

    try:
        print("\nGetting csv text-label train file path:")
        redis_update = {
            "status": REDIS_OPTIONS.STATUS_DATASET_PREPARING,
            "step_2_dataset_start": "[OK]"
        }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        train_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[train_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
        print(f"train_text_lab_csv_path: {train_text_lab_csv_path}")

        print("\nGetting csv text-label file train data:")
        with open(file=train_text_lab_csv_path,
                  mode="r", encoding="utf-8") as train_csv_file:
            csf_text_lab = CsvTextLabel(train_csv_file)
            train_texts = csf_text_lab.get_texts_list_unique()
            train_labels = csf_text_lab.get_labels_list_unique()
            print(f"train_texts [{len(train_texts)}]: {train_texts}")
            print(f"train_labels [{len(train_labels)}]: {train_labels}")

        print("\nCreating training Tensor dataset:")
        datetime_start = datetime.now()
        new_train_dataset = bert_model_inst.create_train_dataset(
            texts_list=train_texts,
            labels_list=train_labels,
            truncation=BERT_TRAIN_OPTIONS.BERT_TOKEN_TRUNCATION,
            padding=BERT_TRAIN_OPTIONS.BERT_TOKEN_PADDING,
            return_tensors=BERT_TRAIN_OPTIONS.BERT_RETURN_TENSOR)
        creating_dataset_time = (datetime.now() - datetime_start).total_seconds()
        creating_dataset_time = round(creating_dataset_time, 1)

        if not new_train_dataset:
            log_text = (f"TrainDataset [ERROR]: get train dataset with"
                        f"method .create_train_dataset() first:\n"
                        f"new_train_dataset: {new_train_dataset}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)

        redis_update = {
            "status": REDIS_OPTIONS.STATUS_TRAIN_START,
            "creating_dataset_time": creating_dataset_time,
            "step_3_dataset_finish": "[OK]",
        }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        background_tasks.add_task(background_train_save_model,
                                  auth_data,
                                  train_model_data,
                                  new_train_dataset,
                                  dataset_name,
                                  train_text_lab_csv_path,
                                  creating_dataset_time)

        json_response = JSONResponse(
            content={
                "message": "BERT model training start [OK]",
                "username": auth_data.username,
                "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                "train dataset path": train_text_lab_csv_path,
                "creating dataset time": creating_dataset_time,
                "dataset_name": dataset_name,
            },
            status_code=status.HTTP_202_ACCEPTED)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"message: BERT model training start [OK]\n"
              f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
              f"model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
              f"model path: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
              f"train dataset path: {train_text_lab_csv_path}\n"
              f"creating dataset time: {creating_dataset_time}\n"
              f"dataset_name: {blue_color}{dataset_name}{reset_color}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router train model [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
