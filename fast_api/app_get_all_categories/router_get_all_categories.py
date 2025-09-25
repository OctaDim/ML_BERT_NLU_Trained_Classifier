# import asyncio
# from functools import partial
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_get_all_categories = APIRouter(prefix=f"/{bert_base_url_name}",
                                           tags=["BERT"])


@router_bert_get_all_categories.post(path="/bert_get_categories_list/",
                                     # TODO: Describe responses here
                                     response_model=None)
async def bert_get_categories_list(
        auth_data: AuthDataBert,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        datetime_start = datetime.now()
        print("\nGetting last saved dataset directory name:")
        inst_last_saved_dataset_path = bert_model_inst.last_saved_dataset_dir
        last_saved_dataset_dir_path, initial_dataset_dir_path = None, None
        if inst_last_saved_dataset_path:
            last_dataset_dir = inst_last_saved_dataset_path
        else:
            last_saved_dataset_dir_path = get_last_saved_dataset_dir_path()
            if last_saved_dataset_dir_path:
                last_dataset_dir = last_saved_dataset_dir_path
            else:
                initial_dataset_dir_path = get_initial_dataset_dir_path()
                if initial_dataset_dir_path:
                    last_dataset_dir = initial_dataset_dir_path
                else:
                    last_dataset_dir = ""
        if not last_dataset_dir:
            log_text = (
                f"BERT Last dataset directory or files not found [ERROR]:\n"
                f"inst_last_saved_dataset_path: {inst_last_saved_dataset_path}\n"
                f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                f"initial_dataset_dir_path: {initial_dataset_dir_path}\n"
                f"last_dataset_dir: {last_dataset_dir}\n")
            print(log_text)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=log_text)

        print("\nGetting non-titled categories list:")
        labels_categories_dir = last_dataset_dir
        labels_categories_file = BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME

        csv_normal_file_path = get_full_file_normal_path(
            all_dir_str_parts=[labels_categories_dir],
            file_name_with_ext=labels_categories_file)

        with open(file=csv_normal_file_path,
                  mode="r", encoding="utf-8") as csv_file:
            csf_lab_cat = CsvLabelCategory(csv_file_obj=csv_file)
            categories_list = csf_lab_cat.get_categories_list_sorted()

        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "getting time": getting_time,
                     "categories_list": categories_list},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"categories_list: {blue_color}{categories_list}{reset_color}\n"
              f"getting_time: {getting_time}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
