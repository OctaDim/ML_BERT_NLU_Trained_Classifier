# import asyncio
# from functools import partial
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_MODEL_NAMES, BERT_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from db_postgres.postgres_queries.qry_get_direct_categ_text_by_acc_dict import (
    get_direct_cat_text_by_acc_dict_qry)
from db_postgres.postgres_queries.qry_get_label_category_dict import (
    get_label_category_dict_qry)
from db_postgres.postgres_queries.qry_get_last_dataset_name_and_dir import (
    get_last_dataset_name_and_dir_qry)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_direct_categories_texts import (
    CsvDirectCategoryText)
from utils_specific.class_csv_labels_categories import (
    CsvLabelCategory)
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
        account_data: AccountDataBert,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    try:
        print("Getting predict and direct categories list by account data:")
        datetime_start = datetime.now()

        print("Postgres DB Getting predict and direct categories list:")
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_predict_lab_cat_dict = await get_label_category_dict_qry(
                ongoing_session=pgs_session,
                reversed_category_label_dict=False)
            pgs_predict_cat_list = list(pgs_predict_lab_cat_dict.values())

            pgs_direct_text_cat_dict = await get_direct_cat_text_by_acc_dict_qry(
                ongoing_session=pgs_session,
                account_id=account_data.account_id,
                account_username=account_data.account_username,
                reversed_direct_text_cat_dict=True)
            pgs_direct_cat_list = list(pgs_direct_text_cat_dict.values())

            print("Postgres DB Merge predict and direct categories lists from db:")
            pgs_merged_cat_list = pgs_predict_cat_list + pgs_direct_cat_list

        if pgs_merged_cat_list:
            categories_list = pgs_merged_cat_list
        else:
            print("Postgres DB Getting last saved dataset directory:")
            pgs_conn = PostgresConnection()
            async with PostgresSession(async_engine=pgs_conn.engine,
                                       log_good_ops=log_pgs_good_ops
                                       ) as pgs_session:
                pgs_last_dataset_data = await get_last_dataset_name_and_dir_qry(
                    ongoing_session=pgs_session)

            if pgs_last_dataset_data:
                # last_dataset_name = pgs_last_dataset_data[0]
                last_dataset_dir = pgs_last_dataset_data[1]
            else:
                print("Getting csv last saved dataset directory name from file:")
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

            print("Getting csv predict non-titled categories list from file:")
            csv_lab_cat_f_name = BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME
            print("Getting csv predict non-titled categories list from file:")
            csv_lab_cat_f_path = get_full_file_normal_path(
                all_dir_str_parts=[last_dataset_dir],
                file_name_with_ext=csv_lab_cat_f_name)
            with open(file=csv_lab_cat_f_path,
                      mode="r", encoding="utf-8") as csv_lab_cat_f:
                csf_lab_cat = CsvLabelCategory(csv_file_obj=csv_lab_cat_f)
                csv_predict_cat_list = csf_lab_cat.get_categories_list_sorted(
                    titled=False)

            print("Getting csv direct non-titled categories list from file:")
            csv_direct_cat_text_f_name = BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME
            csv_direct_cat_text_f_path = get_full_file_normal_path(
                all_dir_str_parts=[last_dataset_dir],
                file_name_with_ext=csv_direct_cat_text_f_name)
            with open(file=csv_direct_cat_text_f_path,
                      mode="r", encoding="utf-8") as csv_cat_text_f:
                csf_cat_text = CsvDirectCategoryText(csv_file_obj=csv_cat_text_f)
                csv_direct_cat_list = csf_cat_text.get_direct_categs_by_acc_list(
                    account_id=account_data.account_id,
                    account_username=account_data.account_username,
                    titled=False)

            print("Merge csv predict and direct categories lists from files:")
            csv_merged_cat_list = csv_predict_cat_list + csv_direct_cat_list
            if csv_merged_cat_list:
                categories_list = csv_merged_cat_list
            else:
                categories_list = []

        unique_categories_list = sorted(list(set(categories_list)))
        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "getting time": getting_time,
                     "categories_list": categories_list,  # Just for compatibility with prev requests to API
                     "unique_categories_list": unique_categories_list},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"categories_list: {blue_color}{categories_list}{reset_color}\n"  # Just for compatibility with prev requests to API
              f"unique_categories_list: {blue_color}{unique_categories_list}{reset_color}\n"
              f"getting_time: {getting_time}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
