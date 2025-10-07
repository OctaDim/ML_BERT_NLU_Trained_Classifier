# import asyncio
# from functools import partial
import copy
import os
import shutil
from datetime import datetime

from fastapi import HTTPException, status

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.settings import BERT_OPTIONS, ALCHEMY_OPTIONS, BASE_DIR
from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_queries.qry_find_cache_label_categ_dict import (
    cache_unique_lab_cat_dict_qry)
from db_postgres.postgres_queries.qry_find_create_dataset import (
    find_create_dataset_qry)
from db_postgres.postgres_queries.qry_save_direct_category_text_list import (
    save_direct_cat_text_list_qry)
from db_postgres.postgres_queries.qry_save_label_text_list import (
    save_label_text_list_qry)
from db_postgres.postgres_queries_helpers.hpr_get_bert_model_data import (
    get_postgres_bert_model_data_hpr)
from fast_api.app_account_data.scheme_account_data import AccountDataBert
from utils_common.normalized_path import (
    get_full_file_normal_path)
from utils_specific.class_csv_direct_categories_texts import (
    CsvDirectCategoryText)
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


async def add_save_multi_text_category_file(
        account_data: AccountDataBert,
        update_text_category_data: list,
        bert_model_inst: ClassifierBERT,
        file_name: str = None,
) -> dict:
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
        pgs_bert_model_data = await get_postgres_bert_model_data_hpr()
        pgs_all_data_flag = pgs_bert_model_data["all_data_flag"]
    else:
        pgs_bert_model_data = None
        pgs_all_data_flag = False

    if not pgs_all_data_flag:
        if bert_model_inst.last_saved_dataset_dir:
            prev_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
        else:
            last_saved_dataset_dir = get_last_saved_dataset_dir_path()
            if last_saved_dataset_dir:
                prev_dataset_dir_path = last_saved_dataset_dir
            else:
                initial_dataset_dir = get_initial_dataset_dir_path()
                if initial_dataset_dir:
                    prev_dataset_dir_path = initial_dataset_dir
                else:
                    prev_dataset_dir_path = ""

        print("Getting previous label-category csv path:")
        prev_lab_cat_csv_path = None
        try:
            prev_lab_cat_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[prev_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

            print("Getting previous label-category dictionary:")
            with open(file=prev_lab_cat_csv_path,
                      mode="r", encoding="utf-8") as prev_lab_cat_csv_f:
                csf_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
                prev_lab_cat_csv_dict = csf_lab_cat.get_label_category_dict()
            print(f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}")  # Too long
            print(f"type(prev_lab_cat_csv_dict): {type(prev_lab_cat_csv_dict)}")
            print(f"len(prev_lab_cat_csv_dict): {len(prev_lab_cat_csv_dict)}")

            if not prev_lab_cat_csv_dict:
                error_log = (f"Empty or wrong label-category csv data [ERROR]:\n"
                             f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}\n"
                             f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            prev_lab_cat_dict = prev_lab_cat_csv_dict
        except Exception as lab_cat_csv_file_error:
            error_log = (f"Getting label-category csv file data [ERROR]:\n"
                         f"error: {lab_cat_csv_file_error}\n"
                         f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}\n"
                         f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        print("Getting previous text-label csv path:")
        prev_text_lab_csv_path = None
        try:
            prev_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[prev_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

            print("Getting previous text-label dictionary:")
            with open(file=prev_text_lab_csv_path,
                      mode="r", encoding="utf-8") as prev_text_lab_csv_f:
                csf_text_lab = CsvTextLabel(prev_text_lab_csv_f)
                prev_text_lab_csv_dict = csf_text_lab.get_text_label_dict()
            # print(f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}")  # Too long
            print(f"type(prev_lab_cat_csv_dict): {type(prev_lab_cat_csv_dict)}")
            print(f"len(prev_lab_cat_csv_dict): {len(prev_lab_cat_csv_dict)}")

            if not prev_text_lab_csv_dict:
                error_log = (f"Empty or wrong text-label csv data [ERROR]:\n"
                             f"prev_text_lab_csv_path: {prev_text_lab_csv_path}\n"
                             f"prev_text_lab_csv_dict: {prev_text_lab_csv_dict}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            prev_text_lab_dict = prev_text_lab_csv_dict
        except Exception as text_lab_csv_file_error:
            error_log = (f"Getting text-label csv file data [ERROR]:\n"
                         f"error: {text_lab_csv_file_error}\n"
                         f"prev_text_lab_csv_path: {prev_text_lab_csv_path}\n"
                         f"prev_text_lab_csv_dict: {prev_text_lab_csv_dict}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        print("Getting previous direct category-text csv path:")
        prev_direct_cat_text_csv_path = None
        try:
            prev_direct_cat_text_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[prev_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)

            print("Getting previous direct category-text dicts list:")
            with open(file=prev_direct_cat_text_csv_path,
                      mode="r", encoding="utf-8"
                      ) as prev_direct_cat_text_csv_f:
                csf_direct_cat_text = CsvDirectCategoryText(
                    csv_file_obj=prev_direct_cat_text_csv_f)
                prev_direct_cat_text_csv_list = csf_direct_cat_text.get_direct_categories_texts_list()
            # print(f"prev_direct_cat_text_csv_list: {prev_direct_cat_text_csv_list}")  # Too long
            print(f"type(prev_direct_cat_text_csv_list): {type(prev_direct_cat_text_csv_list)}")
            print(f"len(prev_direct_cat_text_csv_list): {len(prev_direct_cat_text_csv_list)}")

            if not prev_direct_cat_text_csv_list:
                error_log = (f"Empty or wrong direct category-text csv data [ERROR]:\n"
                             f"prev_direct_cat_text_csv_path: {prev_direct_cat_text_csv_path}\n"
                             f"prev_direct_cat_text_csv_list: {prev_direct_cat_text_csv_list}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
        except Exception as text_lab_csv_file_error:
            error_log = (
                f"Getting direct category-text csv file data [ERROR]:\n"
                f"error: {text_lab_csv_file_error}\n"
                f"prev_direct_cat_text_csv_path: {prev_direct_cat_text_csv_path}\n"
                f"prev_direct_cat_text_csv_list: {prev_direct_cat_text_csv_list}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)
    else:  # All Postgres DB data exists (if pgs_all_data_flag:)
        prev_lab_cat_dict = pgs_bert_model_data["lab_cat_dict"]
        prev_text_lab_dict = pgs_bert_model_data["text_lab_dict"]
        # pgs_lab_text_dicts_list = pgs_bert_model_data["lab_text_dicts_list"]
        prev_dataset_dir = pgs_bert_model_data["dataset_dir"]

        prev_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

        prev_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

        prev_direct_cat_text_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)

    update_lab_cat_list = []
    update_text_lab_list = []
    upd_direct_text_cat_list = []

    upd_lab_cat_dict = copy.copy(prev_lab_cat_dict)
    upd_text_lab_dict = copy.copy(prev_text_lab_dict)

    empty_error_skipped_rows = []  # Just return info
    new_categories_list = []  # Just return info
    new_texts_list = []  # Just return info
    result_list = []  # Just return info

    try:
        print("Group adding multi label-category file:")
        common_datetime_str = str(datetime.now())

        for cur_upd_text_cat in update_text_category_data:
            if len(cur_upd_text_cat) != 2:
                print(f"Current row skipped, not 2 fields number [ERROR]:\n"
                      f"cur_upd_text_cat: {cur_upd_text_cat}\n")
                empty_error_skipped_rows.append(cur_upd_text_cat)
                continue

            cur_upd_text = cur_upd_text_cat[0].strip().lower()
            cur_upd_category = cur_upd_text_cat[1].strip().lower()
            if not cur_upd_text or not cur_upd_category:
                print(f"Current row skipped, empty field value [ERROR]:\n"
                      f"cur_upd_text: {cur_upd_text}\n"
                      f"cur_upd_category: {cur_upd_category}\n")
                empty_error_skipped_rows.append(cur_upd_text_cat)
                continue

            category_exists_flag = cur_upd_category in upd_lab_cat_dict.values()
            text_exists_flag = cur_upd_text in upd_text_lab_dict.keys()
            print(f"category_exists_flag: {category_exists_flag}")
            print(f"text_exists_flag: {text_exists_flag}")

            if category_exists_flag and text_exists_flag:
                result_list.append([f"exists: {cur_upd_category}",
                                    f"exists: {cur_upd_text[:20]}"])  # Just return info
            elif not category_exists_flag and not text_exists_flag:
                new_categories_list.append(cur_upd_category)  # Just return info
                new_texts_list.append(cur_upd_text[:20])  # Just return info
                result_list.append([f"new: {cur_upd_category}",
                                    f"new: {cur_upd_text[:20]}"])  # Just return info

                print("Getting next label new index for new category:")
                next_label_new_index = max(upd_lab_cat_dict.keys()) + 1

                print("Updating lab-cat update list and dict with new category:")
                new_lab_cat_data = (common_datetime_str,
                                    next_label_new_index,
                                    cur_upd_category)
                update_lab_cat_list.append(new_lab_cat_data)
                upd_lab_cat_dict[next_label_new_index] = cur_upd_category

                print("Updating lab-text update list and dict with new text:")
                new_lab_text_data = (common_datetime_str,
                                     next_label_new_index,
                                     cur_upd_text)
                update_text_lab_list.append(new_lab_text_data)
                upd_text_lab_dict[cur_upd_text] = next_label_new_index
            elif category_exists_flag and not text_exists_flag:
                new_texts_list.append(cur_upd_text[:20])  # Just return info
                result_list.append([f"exists: {cur_upd_category}",
                                    f"new: {cur_upd_text[:20]}"])  # Just return info

                print("Getting existing label index of existing category:")
                existing_lab_cat_index = None
                for cur_exist_label, cur_exist_cat in upd_lab_cat_dict.items():
                    if cur_upd_category == cur_exist_cat:
                        existing_lab_cat_index = cur_exist_label

                print("Updating label-text update list with new text:")
                new_lab_text_data = (common_datetime_str,
                                     existing_lab_cat_index,
                                     cur_upd_text)
                upd_text_lab_dict[cur_upd_text] = existing_lab_cat_index
                update_text_lab_list.append(new_lab_text_data)
            elif text_exists_flag and not category_exists_flag:
                new_categories_list.append(f"direct: {cur_upd_category}")  # Just return info
                new_texts_list.append(f"direct: {cur_upd_text[:20]}")  # Just return info
                result_list.append([f"direct: {cur_upd_category}",
                                    f"direct: {cur_upd_text[:20]}"])  # Just return info

                print("Updating cat-text update list with new category-text:")
                cur_direct_category = cur_upd_category
                cur_direct_text = cur_upd_text
                new_direct_cat_text_data = (common_datetime_str,
                                            account_data.account_id,
                                            account_data.account_username,
                                            cur_direct_category,
                                            cur_direct_text)
                upd_direct_text_cat_list.append(new_direct_cat_text_data)

        print("Creating new dataset directory path:")
        new_dataset_dir_path = get_new_dataset_dir_path()
        os.makedirs(name=new_dataset_dir_path, exist_ok=True)
        new_dataset_name = new_dataset_dir_path.split(os.path.sep)[-1]

        print("Group saving multi updated label-category csv file:")
        if update_lab_cat_list:  # New category or categories to add
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_lab_cat_csvf:
                    csv_lab_cat = CsvLabelCategory(new_lab_cat_csvf)
                    csv_lab_cat.add_multi_label_category_rows(
                        upd_label_category_data=update_lab_cat_list)
                lab_cat_csv_path = new_lab_cat_csv_path  # Return info
            else:
                with open(file=prev_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_lab_cat_csvf:
                    csv_lab_cat = CsvLabelCategory(prev_lab_cat_csvf)
                    csv_lab_cat.add_multi_label_category_rows(
                        upd_label_category_data=update_lab_cat_list)
                lab_cat_csv_path = prev_lab_cat_csv_path  # Return info
        else:
            new_lab_cat_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
            shutil.copy2(src=prev_lab_cat_csv_path,
                         dst=new_lab_cat_csv_path)
            lab_cat_csv_path = new_lab_cat_csv_path  # Return info

        print("Group saving multi updated text-label csv file:")
        if update_text_lab_list:
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_text_lab_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
                shutil.copy2(src=prev_text_lab_csv_path,
                             dst=new_text_lab_csv_path)
                with open(file=new_text_lab_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_text_lab_csvf:
                    csv_text_lab = CsvTextLabel(new_text_lab_csvf)
                    csv_text_lab.add_multi_text_label_rows(
                        upd_text_label_data=update_text_lab_list)
                text_lab_csv_path = new_text_lab_csv_path  # Return info
            else:
                with open(file=prev_text_lab_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_text_lab_csvf:
                    csv_text_lab = CsvTextLabel(prev_text_lab_csvf)
                    csv_text_lab.add_multi_text_label_rows(
                        upd_text_label_data=update_text_lab_list)
                text_lab_csv_path = prev_text_lab_csv_path  # Return info
        else:
            new_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)
            text_lab_csv_path = new_text_lab_csv_path  # Return info

        print("Group saving multi updated direct category-text csv file:")
        if upd_direct_text_cat_list:
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_direct_cat_text_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)
                shutil.copy2(src=prev_direct_cat_text_csv_path,
                             dst=new_direct_cat_text_csv_path)
                with open(file=new_direct_cat_text_csv_path, mode="a",
                          encoding="utf-8", newline=""
                          ) as new_direct_cat_txt_csvf:
                    csv_direct_cat_text = CsvDirectCategoryText(
                        csv_file_obj=new_direct_cat_txt_csvf)
                    csv_direct_cat_text.add_multi_direct_cat_text_rows(
                        upd_direct_category_text_data=upd_direct_text_cat_list)
                direct_cat_text_csv_path = new_direct_cat_text_csv_path
            else:
                with open(file=prev_direct_cat_text_csv_path, mode="a",
                          encoding="utf-8", newline=""
                          ) as prev_direct_cat_text_csvf:
                    csv_direct_cat_text = CsvDirectCategoryText(
                        csv_file_obj=prev_direct_cat_text_csvf)
                    csv_direct_cat_text.add_multi_direct_cat_text_rows(
                        upd_direct_category_text_data=upd_direct_text_cat_list)
                direct_cat_text_csv_path = prev_direct_cat_text_csv_path
        else:
            new_direct_cat_text_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)
            shutil.copy2(src=prev_direct_cat_text_csv_path,
                         dst=new_direct_cat_text_csv_path)
            direct_cat_text_csv_path = new_direct_cat_text_csv_path

        print("Saving updated dataset ini file path:\n")
        last_saved_dataset_ini_fpath = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)
        last_saved_dataset_ini_dir = os.path.dirname(
            last_saved_dataset_ini_fpath)
        os.makedirs(name=last_saved_dataset_ini_dir, exist_ok=True)
        with open(file=last_saved_dataset_ini_fpath,
                  mode="w", encoding="utf-8") as dataset_ini_file:
            dataset_ini_file.write(new_dataset_dir_path)

        bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path

        if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
            print("Postgres DB saving lab-cat-text, direct cat-text from file:")
            update_lab_cat_dict = {}
            for cur_row in update_lab_cat_list:
                label_index, text = cur_row[1], cur_row[2]
                update_lab_cat_dict[label_index] = text
            print(f"update_lab_cat_dict: {update_lab_cat_dict}")  # Too long

            update_lab_text_list = []
            for cur_row in update_text_lab_list:
                label_index, text = cur_row[1], cur_row[2]
                cur_lab_text_dict = {"label_index": label_index,
                                     "text": text}
                update_lab_text_list.append(cur_lab_text_dict)
            print(f"update_lab_cat_dict: {update_lab_cat_dict}")  # Too long

            upd_direct_text_cat_list = []
            for cur_row in upd_direct_text_cat_list:
                account_id, account_username = cur_row[1], cur_row[2]
                direct_category, direct_text = cur_row[3], cur_row[4]
                cur_direct_cat_text_dict = {
                    "account_id": account_id,
                    "account_username": account_username,
                    "direct_category": direct_category,
                    "direct_text": direct_text}
                upd_direct_text_cat_list.append(cur_direct_cat_text_dict)
            print(f"upd_direct_text_cat_list: {upd_direct_text_cat_list}")  # Too long

            pgs_conn = PostgresConnection()
            async with PostgresSession(async_engine=pgs_conn.engine,
                                       log_good_ops=log_pgs_good_ops
                                       ) as pgs_session:
                creation_reason = f"uploaded dataset file: {file_name}"

                dataset_id = await find_create_dataset_qry(
                    ongoing_session=pgs_session,
                    dataset_name=new_dataset_name,
                    dataset_csv_dir=new_dataset_dir_path,
                    creation_reason=creation_reason)

                await cache_unique_lab_cat_dict_qry(
                    ongoing_session=pgs_session,
                    dataset_id=dataset_id,
                    label_category_dict=update_lab_cat_dict,
                    creation_reason=creation_reason,
                    save_only_unique=True)
                print(f"Postgres DB labels categories saved [OK]:\n"
                      f"update_lab_cat_dict: {update_lab_cat_dict}\n")

                await save_label_text_list_qry(
                    ongoing_session=pgs_session,
                    label_text_dicts_list=update_lab_text_list,
                    creation_reason=creation_reason,
                    save_only_unique=True)

                await save_direct_cat_text_list_qry(
                    ongoing_session=pgs_session,
                    direct_cat_text_dicts_list=upd_direct_text_cat_list,
                    creation_reason=creation_reason,
                    save_only_unique=False)

        new_csv_files_data = {
            "lab_cat_csv_path": lab_cat_csv_path,
            "text_lab_csv_path": text_lab_csv_path,
            "direct_cat_text_csv_path": direct_cat_text_csv_path,
            "last_saved_dataset_ini_fpath": last_saved_dataset_ini_fpath,
            "empty_error_skipped_rows": empty_error_skipped_rows,
            "new_categories_list": new_categories_list,
            "new_texts_list": new_texts_list,
            "result_list": result_list}
        return new_csv_files_data
    except Exception as error:
        error_log = (f"BERT add and save texts-categories file [ERROR]: "
                     f"error: {error}")
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_log)
