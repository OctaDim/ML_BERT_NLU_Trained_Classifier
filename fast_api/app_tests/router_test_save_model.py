import random
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_instance
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (BASE_DIR, BERT_MODEL_NAMES, BERT_OPTIONS)
from fast_api.app_auth.funcs_auth import verify_username_password
from fast_api.app_auth.scheme_auth import AuthDataTest
from fast_api.app_tests.schemes_test import SaveModelDataTest
from utils_common.normalized_path import get_full_dir_normal_path


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_test_save_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                   tags=["TEST"])


@router_test_save_model.post(path="/test_save_model/",
                             response_model=None)
async def bert_test_save_model(auth_data: AuthDataTest,
                               save_model_data: SaveModelDataTest):
    verify_username_password(username=auth_data.username,
                             password=auth_data.password)

    print("#" * 100)
    if save_model_data.model_save_dir_path:
        model_save_path = save_model_data.model_save_dir_path
    else:
        model_save_path = BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH

    if not model_save_path:
        log_text = (f"Trained Models save dir path not defined [ERROR]: "
                    f"as req param 'model_save_dir_path' or in settings\n"
                    f"SaveModelDataTest.model_save_dir_path: "
                    f"{save_model_data.model_save_dir_path},"
                    f"BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH: "
                    f"{BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)
    try:
        datetime_start = datetime.now()
        datetime_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
        random_str = str(random.randint(10000, 99999))
        prefix = BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_DIR_PREFIX
        new_dir_name = f"{prefix}_{datetime_str}-{random_str}"

        new_model_dir_path = get_full_dir_normal_path(
            [BASE_DIR, BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH, new_dir_name])

        bert_model_instance.save_model(dir_full_path=new_model_dir_path)
        model_saving_time = (datetime.now() - datetime_start).total_seconds()
        model_saving_time = round(model_saving_time, 1)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        log_text = (
            # TODO: "username": username,
            f"BERT Model saved [OK]:\n"
            f"Pretrained Model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
            f"Pretrained Model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
            f"Pretrained Model download dir: {BERT_OPTIONS.BERT_MODELS_DOWNLOAD_PATH}\n"
            f"Trained Model common save dir: {BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH}\n"
            f"Trained Model saved dir path: {blue_color}{new_model_dir_path}{reset_color}\n"
            f"Trained Model saving time: {model_saving_time}")
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
