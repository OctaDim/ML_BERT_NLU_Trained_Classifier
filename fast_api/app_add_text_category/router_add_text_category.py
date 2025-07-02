# import asyncio
# from functools import partial
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_OPTIONS)
from fast_api.app_add_text_category.func_add_save_test_category import add_save_test_category
from fast_api.app_add_text_category.scheme_add_text_category import (
    TextCategoryDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_add_text_category = APIRouter(prefix=f"/{bert_base_url_name}",
                                          tags=["BERT"])


@router_bert_add_text_category.post(path="/bert_add_text_category/",
                                    # TODO: Describe responses here
                                    response_model=None)
async def bert_add_text_category(auth_data: AuthDataBert,
                                 text_category_data: TextCategoryDataBert):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    update_text = text_category_data.update_text
    update_category = text_category_data.update_category

    if not update_text or not update_category:
        log_text = (f"Empty text or category [ERROR]: "
                    f"text_category_data.update_text: {update_text}, "
                    f"text_category_data.update_category: {update_category}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    try:
        update_text = update_text.strip().lower()
        update_category = update_category.strip().lower()

        datetime_start = datetime.now()
        new_csv_files_paths = add_save_test_category(
            update_text=update_text,
            update_category=update_category)
        adding_time = (datetime.now() - datetime_start).total_seconds()
        adding_time = round(adding_time, 1)

        new_lab_cat_csv_path = new_csv_files_paths.get("lab_cat_csv_path")
        new_text_lab_csv_path = new_csv_files_paths.get("text_lab_csv_path")
        json_response = JSONResponse(
            content={
                "message": "BERT text-category csv added [OK]",
                "username": auth_data.username,
                "dataset init": BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH,
                "csv label-category path": new_lab_cat_csv_path,
                "csv text-label path:": new_text_lab_csv_path,
                "adding time": adding_time,
                "added text": update_text,
                "added category": update_category},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"csv label-category path: {new_lab_cat_csv_path}\n"
              f"csv text-label path: {new_text_lab_csv_path}\n"
              f"added text: {blue_color}{update_text}{reset_color}\n"
              f"added category: {blue_color}{update_category}{reset_color}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
