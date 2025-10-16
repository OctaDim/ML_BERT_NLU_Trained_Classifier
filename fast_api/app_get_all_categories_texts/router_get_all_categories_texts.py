# import asyncio
# from functools import partial
from datetime import datetime
from typing import Annotated, Dict

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from db_postgres.postgres_async_conn.pgs_async_connection import PostgresConnection
from db_postgres.postgres_async_conn.postgres_async_session import PostgresSession
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from db_postgres.postgres_queries.qry_get_direct_category_text_by_acc_dict import get_direct_categ_text_by_acc_dict_qry
from db_postgres.postgres_queries.qry_get_label_category_dict import get_label_category_dict_qry
from db_postgres.postgres_queries.qry_get_label_text_dict import get_label_text_dict_qry
from fast_api.app_account_data.scheme_account_data import AccountDataBert
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_get_all_categories_texts = APIRouter(prefix=f"/{bert_base_url_name}",
                                                 tags=["BERT"])


@router_bert_get_all_categories_texts.post(path="/bert_get_categories_texts_dict/",
                                           # TODO: Describe responses here
                                           response_model=None)
async def bert_get_categories_texts_dict(
        auth_data: AuthDataBert,
        account_data: AccountDataBert,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
, log_pgs_good_ops=None) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        print("Getting all dataset texts per category by account data:")
        datetime_start = datetime.now()

        print("Postgres DB Getting predict and direct categories list:")
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_predict_lab_cat_dict = await get_label_category_dict_qry(
                ongoing_session=pgs_session,
                reversed_category_label_dict=False)
            print(11111111111111111111111111111111111111111111111111111)
            print("pgs_predict_lab_cat_dict:", pgs_predict_lab_cat_dict)

            pgs_predict_text_lab_dict = await get_label_text_dict_qry(
                ongoing_session=pgs_session,
                reversed_text_label_dict=True)
            print(22222222222222222222222222222222222222222222222222222)
            print("pgs_predict_text_lab_dict:", pgs_predict_text_lab_dict)

            pgs_predict_text_cat_dict = {}
            for cur_text, cur_label in pgs_predict_text_lab_dict.items():
                cur_category_name = pgs_predict_lab_cat_dict[cur_label]
                pgs_predict_text_cat_dict[cur_text] = cur_category_name
            print(33333333333333333333333333333333333333333333333333333)
            print("pgs_predict_text_cat_dict:", pgs_predict_text_cat_dict)

            pgs_direct_text_cat_dict = await get_direct_categ_text_by_acc_dict_qry(
                ongoing_session=pgs_session,
                account_id=account_data.account_id,
                account_username=account_data.account_username,
                reversed_direct_text_cat_dict=True)
            print(44444444444444444444444444444444444444444444444444444)
            print("pgs_direct_text_cat_dict:", pgs_direct_text_cat_dict)
            # pgs_direct_cat_list = list(pgs_direct_text_cat_dict.values())

            pgs_updated_cat_list_dict = (
                    pgs_predict_text_cat_dict | pgs_direct_text_cat_dict)  # Updating first dict with second one
            print(55555555555555555555555555555555555555555555555555555)
            print("pgs_updated_cat_list_dict:", pgs_updated_cat_list_dict)

            pgs_category_texts_dict = {}
            for cur_text, cur_category in pgs_updated_cat_list_dict.items():
                cur_cat_texts_list = pgs_category_texts_dict.get(cur_category, [])
                cur_cat_texts_list.append(cur_text)
                pgs_category_texts_dict[cur_category] = cur_cat_texts_list
            print(66666666666666666666666666666666666666666666666666666)
            print("pgs_category_texts_dict:", pgs_category_texts_dict)

        if pgs_updated_cat_list_dict:
            categories_list = pgs_updated_cat_list_dict

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
        lab_cat_file_name = BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME
        csv_lab_cat_file_path = get_full_file_normal_path(
            all_dir_str_parts=[last_dataset_dir],
            file_name_with_ext=lab_cat_file_name)

        with open(file=csv_lab_cat_file_path,
                  mode="r", encoding="utf-8") as csv_lab_cat_file:
            csf_lab_cat = CsvLabelCategory(csv_file_obj=csv_lab_cat_file)
            dataset_lab_cat_dict = csf_lab_cat.get_label_category_dict()
        # print(f"dataset_lab_cat_dict => {dataset_lab_cat_dict}")  # Too long
        print(f"len(dataset_lab_cat_dict) => {len(dataset_lab_cat_dict)}")

        lab_txt_file_name = BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME
        csv_lab_txt_file_path = get_full_file_normal_path(
            all_dir_str_parts=[last_dataset_dir],
            file_name_with_ext=lab_txt_file_name)

        with open(file=csv_lab_txt_file_path,
                  mode="r", encoding="utf-8") as csv_lab_txt_file:
            csf_lab_txt = CsvTextLabel(csv_file_obj=csv_lab_txt_file)
            dataset_lab_txt_dict = csf_lab_txt.get_text_label_dict()
        # print(f"dataset_lab_txt_dict => {dataset_lab_txt_dict}")  # Too long
        print(f"len(dataset_lab_txt_dict) => {len(dataset_lab_txt_dict)}")

        # TODO: Decide which option (double loop or single) is faster and keep it
        # Single loop
        csv_category_texts_dict = {}
        for cur_text, cur_label in dataset_lab_txt_dict.items():
            category_name = dataset_lab_cat_dict[cur_label]
            cur_cat_texts_list = csv_category_texts_dict.get(category_name, [])
            cur_cat_texts_list.append(cur_text)
            csv_category_texts_dict[category_name] = cur_cat_texts_list

        # # Double loop
        # csv_category_texts_dict = {}
        # for cur_label, cur_category in dataset_lab_cat_dict.items():
        #     cur_category_texts = []
        #     for cur_text, cur_text_label in dataset_lab_txt_dict.items():
        #         if cur_text_label == cur_label:
        #             cur_category_texts.append(cur_text)
        #     csv_category_texts_dict[cur_category] = cur_category_texts

        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT all texts by categories got [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "getting time": getting_time,
                     # "dataset_lab_cat_dict": dataset_lab_cat_dict,
                     # "dataset_lab_txt_dict": dataset_lab_txt_dict,
                     "category_texts_dict": category_texts_dict
                     },
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"len(category_texts_dict): {len(category_texts_dict)}\n"
              # f"category_texts_dict: {category_texts_dict}\n"  # Too long
              # f"dataset_lab_cat_dict: {dataset_lab_cat_dict}\n"
              # f"dataset_lab_txt_dict: {dataset_lab_txt_dict}\n"
              f"getting_time: {getting_time}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
