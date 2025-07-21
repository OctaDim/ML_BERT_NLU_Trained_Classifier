# import asyncio
# from functools import partial
import redis
import json
from datetime import timedelta
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BASE_DIR, BERT_MODEL_NAMES, BERT_OPTIONS, BERT_TRAIN_OPTIONS)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_save_model.router_bert_save_model import bert_save_model
from fast_api.app_bert_save_model.scheme_bert_save_model import (
    SaveModelAfterTrainBert, SaveModelDataBert)
from fast_api.app_bert_train_model.scheme_bert_train_model import TrainModelDataBert
from utils_common.normalized_path import get_full_dir_normal_path, get_full_file_normal_path
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
        background_tasks: BackgroundTasks,  # class for fastapi background tasks adding and getting
):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    if bert_model_inst.last_saved_dataset_dir:
        train_dataset_dir = bert_model_inst.last_saved_dataset_dir
    else:
        initial_dataset_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
        train_dataset_dir = get_full_dir_normal_path(
            [BASE_DIR, initial_dataset_dir])
        if not (os.path.exists(train_dataset_dir)
                and os.path.isdir(train_dataset_dir)):
            train_dataset_dir = bert_model_inst.last_saved_dataset_dir

    try:
        print("\nPreparing training data set:")
        train_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[train_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
        print(f"train_text_lab_csv_path: {train_text_lab_csv_path}")

        with open(file=train_text_lab_csv_path,
                  mode="r", encoding="utf-8") as train_csv_file:
            csf_text_lab = CsvTextLabel(train_csv_file)
            train_texts = csf_text_lab.get_texts_list_unique()
            train_labels = csf_text_lab.get_labels_list_unique()
            print(f"train_texts [{len(train_texts)}]: {train_texts}")
            print(f"train_labels [{len(train_labels)}]: {train_labels}")

        datetime_start = datetime.now()
        print("\nStart training BERT model:")
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

        background_task_id = str(uuid.uuid4())
        # TODO: REDIS training_statuses[task_id] = {"status": "pending", "progress": 0}

        print("\nModel training:")
        datetime_start = datetime.now()
        bert_model_inst.train(
            train_dataset=new_train_dataset,
            max_training_epochs=BERT_TRAIN_OPTIONS.BERT_TRAIN_MAX_EPOCHS_NUMBER,
            max_cont_100perc_epochs=BERT_TRAIN_OPTIONS.CONTINUOUS_100PERC_EPOCHS,
            batch_size=BERT_TRAIN_OPTIONS.BERT_TRAIN_BATCH_SUZE,
            learning_rate=BERT_TRAIN_OPTIONS.BERT_TRAIN_LEARNING_RATE)
        training_time = (datetime.now() - datetime_start).total_seconds()
        hours, remainder = [int(el) for el in divmod(training_time, 3600)]
        minutes, seconds = [int(el) for el in divmod(remainder, 60)]
        training_time_str = f"{hours} hrs : {minutes} min : {seconds} sec"

        json_response = JSONResponse(
            content={"message": "BERT model training [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "train dataset path": train_text_lab_csv_path,
                     "creating dataset time": creating_dataset_time,
                     "training model time": training_time_str},
            status_code=status.HTTP_202_ACCEPTED)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"train dataset path: {train_text_lab_csv_path}\n"
              f"creating dataset time: {creating_dataset_time}\n"
              f"training model time: {blue_color}{training_time_str}{reset_color}\n")

        if train_model_data.save_model_after_train:
            trained_model_save_dir_path = train_model_data.trained_model_save_dir_path
            save_model_data_bert = SaveModelDataBert(
                model_save_dir_path=trained_model_save_dir_path)
            save_model_after_train_bert = SaveModelAfterTrainBert(
                trained_model_redirected_save_flag=True,
                redirected_train_text_lab_csv_path=train_text_lab_csv_path,
                redirected_creating_dataset_time=creating_dataset_time,
                redirected_training_time=training_time_str)
            # Redirecting to save model view with necessary params
            await bert_save_model(
                auth_data=auth_data,
                save_model_data=save_model_data_bert,
                save_model_after_train_data=save_model_after_train_bert)
        else:
            return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
