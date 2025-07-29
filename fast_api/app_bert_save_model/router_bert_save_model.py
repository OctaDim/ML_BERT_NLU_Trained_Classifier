import os
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BASE_DIR, BERT_MODEL_NAMES, BERT_OPTIONS, REDIS_OPTIONS)
from db_redis.func_redis_save_key_mapping import redis_save_key_mapping_dict
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
                          save_model_data: SaveModelDataBert,
                          save_model_after_train_data: SaveModelAfterTrainBert,
                          dataset_name: str = None):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)

    try:
        print("\nBERT saving model after train process:")
        redis_update = {
            "status": REDIS_OPTIONS.STATUS_MODEL_SAVING_PROCESS,
            "step_7_saving_process": "[OK]",
        }
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

        model_saving_time = (datetime.now() - datetime_start).total_seconds()
        model_saving_time = round(model_saving_time, 1)

        new_model_path_dirs = model_save_path.split(os.sep)
        new_model_name = new_model_path_dirs[-1]  # Same as new model directory name

        redis_update = {
            "status": REDIS_OPTIONS.STATUS_TRAIN_AND_SAVE_FINISH,
            "new_model_name": new_model_name,
            "model_saving_time": model_saving_time,
            "step_8_saving_model_after_train_finish": "[OK]",
        }
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

        if save_model_after_train_data.trained_model_redirected_save_flag:
            log_text = (
                f"{log_text}"
                f"redirected save flag: "
                f"{save_model_after_train_data.trained_model_redirected_save_flag}\n"
                f"train dataset path: "
                f"{save_model_after_train_data.redirected_train_text_lab_csv_path}\n"
                f"creating dataset time: "
                f"{save_model_after_train_data.redirected_creating_dataset_time}\n"
                f"training model time: "
                f"{blue_color}{save_model_after_train_data.redirected_training_time}{reset_color}\n")
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
