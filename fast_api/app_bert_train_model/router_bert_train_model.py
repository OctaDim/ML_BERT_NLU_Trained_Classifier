# import asyncio
# from functools import partial
import os
import uuid
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import (
    APIRouter, status, BackgroundTasks, HTTPException, Depends)
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_OPTIONS, BERT_TRAIN_OPTIONS, BERT_MODEL_NAMES, REDIS_OPTIONS,
    BASE_DIR, STATUSES, ALCHEMY_OPTIONS)
from db_postgres.postgres_conn_async.pgs_async_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn_async.postgres_async_session import (
    PgsAsyncSession)
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from db_postgres.postgres_models.before_reinit_bert_model import (
    BeforeReinitBertModel)
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_find_create_dataset import (
    find_create_dataset_qry)
from db_postgres.postgres_queries.qry_get_label_category_dict import (
    get_label_category_dict_qry)
from db_postgres.postgres_queries.qry_get_label_text_dicts_list import (
    get_label_text_dicts_list_qry)
from db_postgres.postgres_queries.qry_get_last_dataset_name_and_dir import (
    get_last_dataset_name_and_dir_qry)
from db_postgres.postgres_queries.qry_save_new_model_data import (
    save_new_model_data_qry)
from db_redis.redis_funcs.func_redis_save_key_mapping import (
    redis_save_key_mapping_dict)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_train_model.func_train_save_model_background import (
    background_train_save_model)
from fast_api.app_bert_train_model.scheme_bert_train_model import (
    TrainModelDataBert)
from utils_common.normalized_path import (
    get_full_file_normal_path, get_full_dir_normal_path)
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_train_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                    tags=["BERT"])


@router_bert_train_model.post(path="/bert_train_model/",
                              # TODO: Describe responses here
                              response_model=None)
async def bert_train_model(
        auth_data: AuthDataBert,
        account_data: AccountDataBert,
        train_model_data: TrainModelDataBert,
        background_tasks: BackgroundTasks,  # FastAPI Class for background tasks
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    try:
        print("Postgres DB Getting last saved dataset directory and dataset name:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_last_dataset_data = await get_last_dataset_name_and_dir_qry(
                ongoing_session=pgs_session)

        if pgs_last_dataset_data:
            train_dataset_dir = pgs_last_dataset_data[1]
            dataset_name = pgs_last_dataset_data[0]
        else:
            print("Getting csv last saved dataset directory and dataset name:")
            inst_last_saved_dataset_path = bert_model_inst.last_saved_dataset_dir
            last_saved_dataset_dir_path, initial_dataset_dir_path = None, None
            if inst_last_saved_dataset_path:
                train_dataset_dir = inst_last_saved_dataset_path
            else:
                last_saved_dataset_dir_path = get_last_saved_dataset_dir_path()
                if last_saved_dataset_dir_path:
                    train_dataset_dir = last_saved_dataset_dir_path
                else:
                    initial_dataset_dir_path = get_initial_dataset_dir_path()
                    if initial_dataset_dir_path:
                        train_dataset_dir = initial_dataset_dir_path
                    else:
                        train_dataset_dir = ""
            if not train_dataset_dir:
                log_text = (
                    f"BERT Train dataset directory or files not found [ERROR]:\n"
                    f"inst_last_saved_dataset_path: {inst_last_saved_dataset_path}\n"
                    f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                    f"initial_dataset_dir_path: {initial_dataset_dir_path}\n"
                    f"train_dataset_dir: {train_dataset_dir}\n")
                print(log_text)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail=log_text)

            dataset_path_dirs = train_dataset_dir.split(os.sep)
            dataset_name = dataset_path_dirs[-1]  # As dataset files directory name

        train_task_uuid = str(uuid.uuid4())

        redis_update = {
            "train_status": STATUSES.STATUS_MODEL_TRAIN_PENDING_EN,
            "complete_train_status": "",
            "train_task_uuid": train_task_uuid,
            "dataset_name": dataset_name,
            "train_step_1_pending": "[OK]", }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        print("Postgres DB Getting label-category dictionary:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_new_lab_cat_dict = await get_label_category_dict_qry(
                ongoing_session=pgs_session,
                reversed_category_label_dict=False)

        if pgs_new_lab_cat_dict:
            new_lab_cat_dict = pgs_new_lab_cat_dict
        else:
            print("Getting csv label-category train file path:")
            train_lab_cat_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[train_dataset_dir],
                file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
            print(f"train_lab_cat_csv_path: {train_lab_cat_csv_path}")

            print("Getting csv label-category dictionary train data:")
            with open(file=train_lab_cat_csv_path,
                      mode="r", encoding="utf-8") as train_lab_cat_csv_file:
                csf_text_lab = CsvLabelCategory(train_lab_cat_csv_file)
                new_lab_cat_dict = csf_text_lab.get_label_category_dict()
                print(f"new_lab_cat_dict [{len(new_lab_cat_dict)}]: "
                      f"{new_lab_cat_dict}")

            if not new_lab_cat_dict:
                log_text = (f"Empty or wrong label-category csv data [ERROR]: "
                            f"train_lab_cat_csv_path: {train_lab_cat_csv_path}, "
                            f"new_lab_cat_dict: {new_lab_cat_dict}\n")
                print(log_text)
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=log_text)

        print(f"####### bert_model_inst: {bert_model_inst}")
        print(f"####### bert_model_inst.model: {bert_model_inst.model}")
        print(f"####### bert_model_inst.labels: {bert_model_inst.labels}")
        print(f"####### new_lab_cat_dict: {new_lab_cat_dict}")
        print(f"####### bert_model_inst.labels == new_lab_cat_dict: "
              f"{bert_model_inst.labels == new_lab_cat_dict}")

        # TODO: Realize passing the training process if the same categories number
        # if bert_model_inst.labels == new_lab_cat_dict:  # The same labels-categories
        #     pass
        if True:  # Temporary (if different labels-categories and texts-labels)
            print("***************************************************")
            print("*** REINITIALIZING MODEL BEFORE TRAINING (start) **")
            print("***************************************************")

            print(f"####### bert_model_inst.labels: {bert_model_inst.labels}")
            print(f"####### new_lab_cat_dict: {new_lab_cat_dict}")
            redis_update = {
                "train_status": STATUSES.STATUS_MODEL_REINIT_START_EN,
                "train_step_2_reinitialising_before_training_started": "[OK]", }
            redis_error = await redis_save_key_mapping_dict(
                key_name=dataset_name,
                mapping_dict=redis_update,
                expiry_seconds=REDIS_KEY_EXPIRE_TIME)
            if redis_error:
                print(redis_error)

            before_reinit_model_temp_path = get_full_dir_normal_path(
                [BASE_DIR, BERT_OPTIONS.BERT_BEFORE_REINIT_MODEL_TEMP_PATH])
            if not os.path.isdir(before_reinit_model_temp_path):
                os.makedirs(before_reinit_model_temp_path, exist_ok=True)

            error_log = bert_model_inst.save_model(  # Model saving before reinitialising
                model_save_dir_path=before_reinit_model_temp_path,
                dataset_save_dir_path=train_dataset_dir)
            if error_log:
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)

            labels_before = bert_model_inst.model.config.num_labels
            error_log = bert_model_inst.reinitialize_with_new_labels(
                new_labels_categories=new_lab_cat_dict)  # Model reinitialising
            if error_log:
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            labels_after = bert_model_inst.model.config.num_labels

            # error_log = bert_model_inst.load_model(
            #     model_load_dir_path=before_reinit_model_temp_path)  # Model loading after reinitialising
            # if error_log:
            #     print(error_log)
            #     raise HTTPException(
            #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #         detail=error_log)

            print("DB Postgres saving before_reinit_model table data:")
            pgs_conn = PgsAsyncConnection()
            async with PgsAsyncSession(engine=pgs_conn.engine,
                                       log_good_ops=log_pgs_good_ops
                                       ) as pgs_session:
                creation_reason = f"reserved before train: {dataset_name}"

                customer_id = await find_create_customer_qry(
                    ongoing_session=pgs_session,
                    account_username=account_data.account_username,
                    account_id=account_data.account_id,
                    creation_reason=creation_reason)

                dataset_id = await find_create_dataset_qry(
                    ongoing_session=pgs_session,
                    dataset_name=dataset_name,
                    customer_id=customer_id,
                    dataset_csv_dir=train_dataset_dir,
                    creation_reason=creation_reason)

                update_data = {
                    "dataset_id": dataset_id,
                    "customer_id": customer_id,
                    "dataset_name": dataset_name,
                    "temp_model_dir": before_reinit_model_temp_path,
                    "labels_before": labels_before,
                    "labels_after": labels_after,
                    "creation_reason": creation_reason}
                await save_new_model_data_qry(
                    ModelClassORM=BeforeReinitBertModel,
                    ongoing_session=pgs_session,
                    new_data=update_data)

            redis_update = {
                "train_status": STATUSES.STATUS_MODEL_REINIT_FINISH_EN,
                "train_step_3_reinitialising_before_training_finished": "[OK]", }
            redis_error = await redis_save_key_mapping_dict(
                key_name=dataset_name,
                mapping_dict=redis_update,
                expiry_seconds=REDIS_KEY_EXPIRE_TIME)
            if redis_error:
                print(redis_error)

            print("***************************************************")
            print("**** REINITIALIZING MODEL BEFORE TRAINING (end) ***")
            print("***************************************************")

        redis_update = {
            "train_status": STATUSES.STATUS_DATASET_CREATION_START_EN,
            "train_step_4_dataset_creation_started": "[OK]", }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        print("Getting csv text-label train file path:")
        train_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[train_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

        print("Postgres DB Getting text-label train data:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_lab_text_dicts_list = await get_label_text_dicts_list_qry(
                ongoing_session=pgs_session)

        if pgs_lab_text_dicts_list:
            train_texts = []
            train_labels = []
            for cur_lab_text_dict in pgs_lab_text_dicts_list:
                train_texts.append(cur_lab_text_dict["text"])
                train_labels.append(cur_lab_text_dict["label_index"])
            # train_text_lab_csv_path = get_full_file_normal_path(
            #     all_dir_str_parts=[train_dataset_dir],
            #     file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
        else:
            # print("Getting csv text-label train file path:")
            # train_text_lab_csv_path = get_full_file_normal_path(
            #     all_dir_str_parts=[train_dataset_dir],
            #     file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
            print(f"train_text_lab_csv_path: {train_text_lab_csv_path}")

            print("Getting csv text-label file train data:")
            with open(file=train_text_lab_csv_path,
                      mode="r", encoding="utf-8") as train_text_lab_csv_file:
                csf_text_lab = CsvTextLabel(train_text_lab_csv_file)
                train_texts = csf_text_lab.get_texts_list_unique()
                train_labels = csf_text_lab.get_labels_list_unique()
        print(f"train_texts [{len(train_texts)}]: {train_texts[:5]}.......")
        print(f"train_labels [{len(train_labels)}]: {train_labels}")

        print("Creating training Tensor dataset:")
        datetime_start = datetime.now()
        new_train_dataset = bert_model_inst.create_train_dataset(
            texts_list=train_texts,
            labels_list=train_labels,
            truncation=BERT_TRAIN_OPTIONS.BERT_TOKEN_TRUNCATION,
            padding=BERT_TRAIN_OPTIONS.BERT_TOKEN_PADDING,
            return_tensors=BERT_TRAIN_OPTIONS.BERT_RETURN_TENSOR)
        print(f"new_train_dataset: {new_train_dataset[:5]}")
        creating_dataset_time = (datetime.now() - datetime_start).total_seconds()
        creating_dataset_time = round(creating_dataset_time, 1)

        redis_update = {
            "train_status": STATUSES.STATUS_DATASET_CREATION_FINISH_EN,
            "creating_dataset_time": creating_dataset_time,
            "train_step_5_dataset_creation_finished": "[OK]", }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        if not new_train_dataset:
            log_text = (f"TrainDataset [ERROR]: get train dataset with"
                        f"method .create_train_dataset() first:\n"
                        f"new_train_dataset: {new_train_dataset}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)

        redis_update = {
            "train_status": STATUSES.STATUS_MODEL_TRAIN_START_EN,
            "train_step_6_model_training_started": "[OK]", }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        print("####### BEFORE BACKGROUND TRAIN AND SAVE MODEL")
        background_tasks.add_task(background_train_save_model,
                                  auth_data,
                                  account_data,
                                  train_model_data,
                                  new_train_dataset,
                                  dataset_name,
                                  train_text_lab_csv_path,
                                  creating_dataset_time,
                                  bert_model_inst)
        print("####### AFTER START BACKGROUND TRAIN AND SAVE MODEL")

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
                "current_status": STATUSES.STATUS_MODEL_TRAIN_START_EN,
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
              f"train_text_lab_csv_path: {train_text_lab_csv_path}\n"
              f"creating_dataset_time: {creating_dataset_time}\n"
              f"dataset_name: {blue_color}{dataset_name}{reset_color}\n")
        print("####### PRELIMINARY 202 RESPONSE AFTER BACKGROUND TRAINING START")
        return json_response
    except Exception as error:
        log_text = f"BERT router train model [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
