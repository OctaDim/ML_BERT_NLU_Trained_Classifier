# import asyncio
# from functools import partial
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_OPTIONS
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from fast_api.app_add_single_category.func_add_single_category import (
    add_save_single_category)
from fast_api.app_add_single_category.scheme_add_single_category import (
    SingleCategoryDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_add_single_category = APIRouter(prefix=f"/{bert_base_url_name}",
                                            tags=["BERT"])


@router_bert_add_single_category.post(path="/bert_add_single_category/",
                                      # TODO: Describe responses here
                                      response_model=None)
async def bert_add_single_category(
        auth_data: AuthDataBert,
        category_data: SingleCategoryDataBert,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    upd_single_category = category_data.update_category.strip().lower()

    if not upd_single_category:
        log_text = (f"Empty category value [ERROR]:\n"
                    f"single_category_data.single_category_data:"
                    f"{upd_single_category}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    try:
        datetime_start = datetime.now()
        new_csv_files_data = await add_save_single_category(
            update_category=upd_single_category,
            bert_model_inst=bert_model_inst)
        adding_time = (datetime.now() - datetime_start).total_seconds()
        adding_time = round(adding_time, 1)

        new_lab_cat_csv_path = new_csv_files_data.get("lab_cat_csv_path")
        new_text_lab_csv_path = new_csv_files_data.get("text_lab_csv_path")
        dataset_ini_file_path = new_csv_files_data.get("last_saved_dataset_ini_fpath")
        new_category = new_csv_files_data.get("new_category")
        json_response = JSONResponse(
            content={
                "message": "BERT text-category csv added [OK]",
                "username": auth_data.username,
                "dataset init": BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH,
                "csv label-category path": new_lab_cat_csv_path,
                "csv text-label path:": new_text_lab_csv_path,
                "dataset ini file path": dataset_ini_file_path,
                "adding time": adding_time,
                "added single category": upd_single_category,
                "new_category": new_category},
            status_code=status.HTTP_200_OK)

        green_color = CONSOLE_COLORS.BRIGHT_GREEN
        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(
            f"BERT response.body: {json_response.body}\n"
            f"BERT response.status_code: {json_response.status_code}\n"
            f"username: {auth_data.username}\n"
            f"csv label-category path: {new_lab_cat_csv_path}\n"
            f"csv text-label path: {new_text_lab_csv_path}\n"
            f"dataset ini file path: {dataset_ini_file_path}\n"
            f"added single category: {green_color}{upd_single_category}{reset_color}\n"
            f"new category: {blue_color}{new_category}{reset_color}")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
