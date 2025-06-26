# import asyncio
# from functools import partial
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import BASE_DIR, BERT_MODEL_NAMES, BERT_OPTIONS
from fast_api.app_auth.funcs_auth import verify_product_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_get_categories_list = APIRouter(prefix=f"/{bert_base_url_name}",
                                            tags=["BERT"])


@router_bert_get_categories_list.post(path="/bert_get_categories_list/",
                                      # TODO: Describe responses here
                                      response_model=None)
async def bert_get_categories_list(auth_data: AuthDataBert):
    verify_product_username_password(username=auth_data.username,
                                     password=auth_data.password)
    try:
        print("\nGetting titled categories list:")
        labels_categories_dir = BERT_OPTIONS.BERT_LABELS_CATEGORIES_CSV_PATH
        labels_categories_file = BERT_OPTIONS.BERT_LABELS_CATEGORIES_CSV_NAME
        csv_normal_file_path = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR, labels_categories_dir],
            file_name_with_ext=labels_categories_file)

        datetime_start = datetime.now()
        with open(csv_normal_file_path, mode="r", encoding="utf-8") as csv_file:
            csf_lab_cat = CsvLabelCategory(csv_file_obj=csv_file)
            categories_list = csf_lab_cat.get_categories_list_sorted()

        # predicted_category = bert_model_instance.predict(text_phrase)
        # prepared_sync_func = partial(bert_model_instance.predict,
        #                              text=text_phrase)
        # predicted_category = await asyncio.to_thread(prepared_sync_func)  # Exec prepared func

        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised: [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_MODELS_DOWNLOAD_PATH,
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
