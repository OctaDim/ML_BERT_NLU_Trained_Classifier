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
    BERT_OPTIONS, BERT_TRAIN_OPTIONS, BERT_MODEL_NAMES,
    REDIS_OPTIONS, BASE_DIR, STATUSES)
from db_postgres.postgres_models.before_reinit_bert_model import (
    BeforeReinitBertModel)
from db_postgres.postgres_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)
from db_redis.redis_funcs.func_redis_save_key_mapping import (
    redis_save_key_mapping_dict)
from fast_api.app_account_data.func_verify_create_customer import (
    verify_create_customer)
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
        background_tasks: BackgroundTasks  # FastAPI Class for background tasks
):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)

    print("\nGetting or creating customer record and customer id:")
    account_username = account_data.account_username
    account_id = account_data.account_id
    customer_id = await verify_create_customer(
        account_username=account_username,
        account_id=account_id)

    print("\nGetting last saved dataset directory name:")
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

    try:
        print("\nGetting csv label-category train file path:")
        train_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[train_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
        print(f"train_lab_cat_csv_path: {train_lab_cat_csv_path}")

        print("\nGetting csv label-category file data:")
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
        if True:  # Different labels-categories
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

            error_log = bert_model_inst.save_model(
                dir_full_path=before_reinit_model_temp_path)  # Model saving before reinitialising
            if error_log:
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)

            labels_before = bert_model_inst.model.config.num_labels
            error_log = bert_model_inst.reinitialize_with_new_labels(
                new_labels=new_lab_cat_dict)  # Model reinitialising
            if error_log:
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            labels_after = bert_model_inst.model.config.num_labels

            # error_log = bert_model_inst.load_model(
            #     dir_full_path=before_reinit_model_temp_path)  # Model loading after reinitialising
            # if error_log:
            #     print(error_log)
            #     raise HTTPException(
            #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #         detail=error_log)

            print("\nDB Postgres saving before_reinit_model table data:")
            async with pgs_conn.async_session() as pgs_session:
                new_model_obj = BeforeReinitBertModel()
                update_data = {
                    "customer_id": customer_id,
                    "temp_model_dir": before_reinit_model_temp_path,
                    "dataset_name": dataset_name,
                    "labels_before": labels_before,
                    "labels_after": labels_after,
                    "status": "reinitialized"}
                await merge_obj_to_ongoing_session(
                    ongoing_session=pgs_session,
                    object_to_merge=new_model_obj,
                    new_update_data=update_data)

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

        print("\nGetting csv text-label train file path:")
        redis_update = {
            "train_status": STATUSES.STATUS_DATASET_CREATION_START_EN,
            "train_step_4_dataset_creation_started": "[OK]", }
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
                  mode="r", encoding="utf-8") as train_text_lab_csv_file:
            csf_text_lab = CsvTextLabel(train_text_lab_csv_file)
            train_texts = csf_text_lab.get_texts_list_unique()
            train_labels = csf_text_lab.get_labels_list_unique()
            print(f"train_texts [{len(train_texts)}]: {train_texts[:25]},..........")
            print(f"train_labels [{len(train_labels)}]: {train_labels[:25]},..........")

        print("\nCreating training Tensor dataset:")
        datetime_start = datetime.now()
        new_train_dataset = bert_model_inst.create_train_dataset(
            texts_list=train_texts,
            labels_list=train_labels,
            truncation=BERT_TRAIN_OPTIONS.BERT_TOKEN_TRUNCATION,
            padding=BERT_TRAIN_OPTIONS.BERT_TOKEN_PADDING,
            return_tensors=BERT_TRAIN_OPTIONS.BERT_RETURN_TENSOR)
        print(f"new_train_dataset: {new_train_dataset[:25]}")
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

        print("\n####### BEFORE BACKGROUND TRAIN AND SAVE MODEL")
        background_tasks.add_task(background_train_save_model,
                                  auth_data,
                                  account_data,
                                  train_model_data,
                                  new_train_dataset,
                                  dataset_name,
                                  train_text_lab_csv_path,
                                  creating_dataset_time)
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
