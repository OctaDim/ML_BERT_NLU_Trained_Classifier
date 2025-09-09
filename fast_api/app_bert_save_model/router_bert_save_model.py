import os
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BASE_DIR, BERT_MODEL_NAMES, BERT_OPTIONS, REDIS_OPTIONS, STATUSES)
from db_postgres.postgres_models.trained_bert_model import (
    TrainedBertModel)
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
from fast_api.app_bert_save_model.scheme_bert_save_model import (
    SaveModelAfterTrainBert, SaveModelDataBert)
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_save_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                   tags=["BERT"])


@router_bert_save_model.post(path="/bert_save_model/",
                             # TODO: Describe responses here
                             response_model=None)
async def bert_save_model(auth_data: AuthDataBert,
                          account_data: AccountDataBert,
                          save_model_data: SaveModelDataBert,
                          save_model_after_train_data: SaveModelAfterTrainBert,
                          dataset_name: str = None):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)

    print("\nGetting or creating customer record and customer id:")
    account_username = account_data.account_username
    account_id = account_data.account_id
    customer_id = await verify_create_customer(
        account_username=account_username,
        account_id=account_id)

    print("\nBERT saving model without train or after train process:")
    save_after_train_flag = save_model_after_train_data.trained_model_redirected_save_flag
    try:
        if save_after_train_flag:
            redis_update = {
                "train_status": STATUSES.STATUS_TRAINED_MODEL_SAVE_PROCESS_EN,
                "train_step_10_saving_model_after_train_in_process": "[OK]", }
            redis_error = await redis_save_key_mapping_dict(
                key_name=dataset_name,
                mapping_dict=redis_update,
                expiry_seconds=REDIS_KEY_EXPIRE_TIME)
            if redis_error:
                print(redis_error)

        if save_model_data.model_save_dir_path:
            model_save_path = save_model_data.model_save_dir_path
        else:
            datetime_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
            random_str = str(random.randint(10000, 99999))
            prefix = BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_DIR_PREFIX
            new_dir_name = f"{prefix}_{datetime_str}-{random_str}"
            model_save_path = get_full_dir_normal_path(
                [BASE_DIR, BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH, new_dir_name])
    except Exception as error:
        log_text = (f"Creating new trained models save dir path [ERROR]: "
                    f"error: {error}\n"
                    f"save_model_data.model_save_dir_path: "
                    f"{save_model_data.model_save_dir_path},"
                    f"BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH: "
                    f"{BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    if not model_save_path:
        log_text = (f"Trained Models save dir path not defined [ERROR]: "
                    f"as req param 'model_save_dir_path' or in settings\n"
                    f"save_model_data.model_save_dir_path: "
                    f"{save_model_data.model_save_dir_path},"
                    f"BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH: "
                    f"{BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)
    try:
        datetime_start = datetime.now()
        error_log = bert_model_inst.save_model(
            dir_full_path=model_save_path)
        # TODO: Make saving learning dataset into the saved model dir also
        #  to have opportunity to load model and to load corresponding
        #  dataset for the model

        if error_log:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        last_saved_model_ini_fpath = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_MODEL_INI_FILE_PATH)

        last_saved_model_ini_fdir = os.path.dirname(
            last_saved_model_ini_fpath)
        os.makedirs(name=last_saved_model_ini_fdir, exist_ok=True)

        with open(file=last_saved_model_ini_fpath,
                  mode="w", encoding="utf-8") as model_ini_file:
            model_ini_file.write(model_save_path)

        print("\nDB Postgres saving trained_model table data:")
        if save_after_train_flag:
            pgs_status = "trained+saved"
        else:
            pgs_status = "saved"
        async with pgs_conn.async_session() as pgs_session:
            new_trained_model_obj = TrainedBertModel()
            trained_model_upd_data = {
                "customer_id": customer_id,
                "model_directory": model_save_path,
                "dataset_name": dataset_name,
                "status": pgs_status}
            await merge_obj_to_ongoing_session(
                ongoing_session=pgs_session,
                object_to_merge=new_trained_model_obj,
                new_update_data=trained_model_upd_data)

        model_saving_time = (datetime.now() - datetime_start).total_seconds()
        model_saving_time = round(model_saving_time, 1)

        new_model_path_dirs = model_save_path.split(os.sep)
        new_model_name = new_model_path_dirs[-1]  # Same as new model directory name

        if save_after_train_flag:
            redis_update = {
                "train_status": STATUSES.STATUS_TRAINED_MODEL_SAVE_FINISH_EN,
                "train_complete_status": "complete",
                "new_model_name": new_model_name,
                "model_saving_time": model_saving_time,
                "train_step_11_saving_model_after_training_finished": "[OK]", }
            redis_error = await redis_save_key_mapping_dict(
                key_name=dataset_name,
                mapping_dict=redis_update,
                expiry_seconds=REDIS_KEY_EXPIRE_TIME)
            if redis_error:
                print(redis_error)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        log_text = (
            f"BERT Model saved [OK]:\n"
            f"username: {auth_data.username}\n"
            f"Pretrained Model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
            f"Pretrained Model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
            f"Pretrained Model download dir: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
            f"Trained Model common save dir: {BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}\n"
            f"Trained Model saved dir path: {blue_color}{model_save_path}{reset_color}\n"
            f"Trained Model saving time: {model_saving_time}\n")

        if save_after_train_flag:
            log_text = (
                f"{log_text}\n"
                f"save after train redirected flag: {save_after_train_flag}\n"
                f"train dataset path: {save_model_after_train_data.redirected_train_text_lab_csv_path}\n"
                f"creating dataset time: {save_model_after_train_data.redirected_creating_dataset_time}\n"
                f"training model time: {blue_color}{save_model_after_train_data.redirected_training_time}{reset_color}\n")
        print(log_text)
        json_response = JSONResponse(
            content={"message": log_text},
            status_code=status.HTTP_200_OK)
        return json_response
    except Exception as error:
        log_text = f"BERT Model not saved [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
