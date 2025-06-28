import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BASE_DIR, BERT_MODEL_NAMES, BERT_OPTIONS
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_load_model.scheme_bert_load_model import LoadModelDataBert
from utils_common.normalized_path import get_full_dir_normal_path


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_load_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                   tags=["BERT"])


@router_bert_load_model.post(path="/bert_load_model/",
                             response_model=None)
async def bert_load_model(auth_data: AuthDataBert,
                          load_model_data: LoadModelDataBert):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    print("#" * 100)
    model_path_file_saved = ""  # TODO: Path from file or MongoDB here

    if load_model_data.model_load_dir_path:
        model_load_path = load_model_data.model_load_dir_path
    elif bert_model_inst.last_saved_model_dir:
        model_load_path = bert_model_inst.last_saved_model_dir
    elif model_path_file_saved:
        model_load_path = model_path_file_saved
    else:
        initial_model_dir = BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH
        model_load_path = get_full_dir_normal_path(
            [BASE_DIR, initial_model_dir])

    if not all([os.path.exists(model_load_path),
                os.path.isdir(model_load_path)]):
        log_text = (f"BERT Model load dir path not found [ERROR]: "
                    f"model_load_path: {model_load_path}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)

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
        error_log = bert_model_inst.load_model(
            dir_full_path=normal_model_load_path)
        if error_log:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

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
