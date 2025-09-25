from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from fast_api.app_auth.funcs_auth import verify_test_username_password
from fast_api.app_tests.schemes_test import (
    AuthDataTest, LoadModelDataTest)
from utils_common.normalized_path import get_full_dir_normal_path

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_test_load_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                   tags=["TEST"])


@router_test_load_model.post(path="/test_load_model/",
                             response_model=None)
async def bert_test_load_model(
        auth_data: AuthDataTest,
        load_model_data: LoadModelDataTest,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_test_username_password(username=auth_data.username,
                                  password=auth_data.password)

    print("#" * 100)
    if load_model_data.model_load_dir_path:
        model_load_path = load_model_data.model_load_dir_path
    else:
        model_load_path = bert_model_inst.last_saved_model_dir

    if not model_load_path:
        log_text = (f"BERT Model load dir path not defined [ERROR]: "
                    f"as req param 'model_load_dir_path' "
                    f"or method save_model() not called first\n"
                    f"load_model_data.model_load_dir_path: "
                    f"{load_model_data.model_load_dir_path}, "
                    f"bert_model_instance.last_saved_model_path: "
                    f"{bert_model_inst.last_saved_model_dir}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)
    try:
        normal_model_load_path = get_full_dir_normal_path([model_load_path, ])

        datetime_start = datetime.now()
        bert_model_inst.load_model(dir_full_path=normal_model_load_path)
        model_load_time = (datetime.now() - datetime_start).total_seconds()
        model_load_time = round(model_load_time, 1)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        log_text = (
            f"BERT Model loaded [OK]:\n"
            f"username: {auth_data.username}\n"
            f"Pretrained Model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
            f"Pretrained Model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
            f"Pretrained Model download dir: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
            f"Trained Model common load dir: {BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}\n"
            f"Trained Model loaded dir path: {blue_color}{normal_model_load_path}{reset_color}\n"
            f"Trained Model loading time: {model_load_time}\n")
        print(log_text)

        json_response = JSONResponse(
            content={"message": log_text},
            status_code=status.HTTP_200_OK)
        return json_response
    except Exception as error:
        log_text = f"BERT Model not loaded [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
