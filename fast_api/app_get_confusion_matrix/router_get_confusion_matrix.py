# import asyncio
# from functools import partial
import base64
import os.path
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS, BASE_DIR
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_get_confusion_matrix.scheme_get_confusion_matrix import (
    ConfusionMatrixData)
from utils_common.normalized_path import get_full_file_normal_path

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_get_confusion_matrix = APIRouter(prefix=f"/{bert_base_url_name}",
                                             tags=["BERT"])


@router_bert_get_confusion_matrix.post(path="/bert_get_confusion_matrix/",
                                       # TODO: Describe responses here
                                       response_model=None)
async def bert_get_confusion_matrix_img(auth_data: AuthDataBert,
                                        conf_mtrx_data: ConfusionMatrixData):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        print("\nGetting confusion matrix filename:")
        datetime_start = datetime.now()
        conf_mtrx_filename = conf_mtrx_data.conf_mtrx_filename
        if not conf_mtrx_filename:
            log_text = (f"Confusion matrix img filename not defined [ERROR]: "
                        f"conf_mtrx_filename: {conf_mtrx_filename}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=log_text)

        print("\nGetting confusion matrix filename path:")
        conf_mtrx_save_dir = BERT_OPTIONS.BERT_CONFUSION_MATRICES_IMAGES_PATH
        conf_mtrx_img_file_path = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR, conf_mtrx_save_dir],
            file_name_with_ext=conf_mtrx_filename)

        if not os.path.isfile(conf_mtrx_img_file_path):
            log_text = (f"Confusion matrix image file not found [ERROR]:\n"
                        f"conf_mtrx_filename: {conf_mtrx_filename}\n"
                        f"conf_mtrx_img_file_path: {conf_mtrx_img_file_path}\n")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)

        print("\nReading confusion matrix filename:")
        with open(conf_mtrx_img_file_path, "rb") as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode("utf-8")
        img_base64_content = f"data:image/png;base64,{img_base64}"
        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_content = {
            "message": "BERT getting confusion matrix image [OK]",
            "username": auth_data.username,
            "model init": BERT_OPTIONS.BERT_MODEL_INIT,
            "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
            "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
            "getting_time": getting_time,
            "img_base64_content": img_base64_content,
            "conf_mtrx_filename": conf_mtrx_filename,
            "conf_mtrx_img_file_path": conf_mtrx_img_file_path}
        json_response = JSONResponse(
            content=json_content,
            status_code=status.HTTP_200_OK)

        print(f"BERT response message: {json_content.get('message')}\n"
              f"BERT response.body keys: {json_content.keys()}\n"
              # f"BERT response.body: {json_response.body}\n"  # Long to log
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"getting_time: {getting_time}\n"
              # f"img_base64_content: {img_base64_content}\n"  # Too long
              f"conf_mtrx_filename: {conf_mtrx_filename}\n"
              f"conf_mtrx_img_file_path: {conf_mtrx_img_file_path}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT router get confusion matrix image [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
