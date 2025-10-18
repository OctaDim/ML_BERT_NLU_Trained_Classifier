# import asyncio
# from functools import partial
import os
import shutil

from fastapi import HTTPException, status

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.settings import (
    BASE_DIR, BERT_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_queries.qry_find_cache_label_categ_dict import (
    cache_unique_lab_cat_dict_qry)
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_find_create_dataset import (
    find_create_dataset_qry)
from db_postgres.postgres_queries.qry_save_direct_category_text_list import (
    save_direct_cat_text_list_qry)
from db_postgres.postgres_queries.qry_save_label_text_dict import (
    save_unique_text_lab_dict_qry)
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
from utils_specific.get_new_dataset_dir_path import (
    get_new_dataset_rand_dir_path)


async def add_save_single_text_category(
        account_data: AccountDataBert,
        update_text: str,
        update_category: str,
        bert_model_inst: ClassifierBERT
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

            print("Getting previous csv label-category dictionary:")
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

            print("Getting previous csv text-label dictionary:")
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
                file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME)

            print("Getting previous csv category-text dicts list:")
            with open(file=prev_direct_cat_text_csv_path,
                      mode="r", encoding="utf-8") as prev_direct_cat_text_csv_f:
                csf_direct_cat_text = CsvDirectCategoryText(prev_text_lab_csv_f)
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
            file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME)

    new_category = None
    new_text = None
    lab_cat_csv_path = None
    text_lab_csv_path = None
    direct_cat_text_csv_path = None

    try:
        print("Creating new dataset directory path:")
        new_dataset_dir_path = get_new_dataset_rand_dir_path()
        new_dataset_name = new_dataset_dir_path.split(os.path.sep)[-1]

        category_exists_flag = update_category in prev_lab_cat_dict.values()
        text_exists_flag = update_text in prev_text_lab_dict.keys()
        print(f"category_exists_flag: {category_exists_flag}")
        print(f"text_exists_flag: {text_exists_flag}")

        if category_exists_flag and text_exists_flag:
            new_category = "category already exists"  # Just return info
            new_text = "text already exists"  # Just return info

            print("Saving existing label-category data into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing lab-cat:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                lab_cat_csv_path = new_lab_cat_csv_path  # Return info
            else:  # Keep old csv file
                print("Keeping old csv file without adding existing label-category:")
                lab_cat_csv_path = prev_lab_cat_csv_path  # Return info

            print("Saving existing text-label data into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing text-label:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_text_lab_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
                shutil.copy2(src=prev_text_lab_csv_path,
                             dst=new_text_lab_csv_path)
                text_lab_csv_path = new_text_lab_csv_path  # Return info
            else:  # Keep old csv file
                print("Keeping old csv file without adding existing text-label:")
                text_lab_csv_path = prev_text_lab_csv_path  # Return info

            print("Saving existing direct category-text data into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing direct cat-text:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_direct_cat_text_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME)
                shutil.copy2(src=prev_direct_cat_text_csv_path,
                             dst=new_direct_cat_text_csv_path)
                direct_cat_text_csv_path = new_direct_cat_text_csv_path  # Return info
            else:  # Keep old csv file
                print("Keeping old csv file without adding existing direct cat-text:")
                direct_cat_text_csv_path = prev_direct_cat_text_csv_path  # Return info
        elif not category_exists_flag and not text_exists_flag:  # new cat and new text
            print("Getting next label new index for new category:")
            next_label_new_index = max(prev_lab_cat_dict.keys()) + 1

            print("Getting next label-category dict with new category:")
            new_lab_cat_dict = {next_label_new_index: update_category}

            print("Creating new text-label dict:")
            new_text_lab_dict = {update_text: next_label_new_index}

            new_category = update_category  # Just return info
            new_text = update_text  # Just return info

            print("Saving new label-category into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv lab-cat file
                print("Copying and updating new csv file with adding new lab-cat:")
                os.makedirs(name=new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_lab_cat_csv_f:
                    csv_lab_cat = CsvLabelCategory(new_lab_cat_csv_f)
                    csv_lab_cat.add_single_label_category_row(
                        new_label=next_label_new_index,
                        new_category=update_category)
                lab_cat_csv_path = new_lab_cat_csv_path  # Return info
            else:  # Append existing lab-cat csv file
                print("Appending existing csv file with adding new label-category:")
                with open(file=prev_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_lab_cat_csv_f:
                    csv_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
                    csv_lab_cat.add_single_label_category_row(
                        new_label=next_label_new_index,
                        new_category=update_category)
                lab_cat_csv_path = prev_lab_cat_csv_path  # Return info

            print("Saving new text-label into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new txt-lab csv file
                print("Copying and creating new csv file with adding new text-label:")
                os.makedirs(name=new_dataset_dir_path, exist_ok=True)
                new_text_lab_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
                shutil.copy2(src=prev_text_lab_csv_path,
                             dst=new_text_lab_csv_path)
                with open(file=new_text_lab_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_text_lab_csv_f:
                    csv_text_lab = CsvTextLabel(new_text_lab_csv_f)
                    csv_text_lab.add_single_text_label_row(
                        new_text=update_text,
                        new_label=next_label_new_index)
                text_lab_csv_path = new_text_lab_csv_path
            else:  # Append existing txt-lab csv file
                print("Appending old csv file with adding new text-label:")
                with open(file=prev_text_lab_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_text_lab_csv_f:
                    csv_text_lab = CsvTextLabel(prev_text_lab_csv_f)
                    csv_text_lab.add_single_text_label_row(
                        new_text=update_text,
                        new_label=next_label_new_index)
                text_lab_csv_path = prev_text_lab_csv_path

            print("Saving existing direct category-text data into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing direct cat-text:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_direct_cat_text_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME)
                shutil.copy2(src=prev_direct_cat_text_csv_path,
                             dst=new_direct_cat_text_csv_path)
                direct_cat_text_csv_path = new_direct_cat_text_csv_path  # Return info
            else:  # Keep existing csv file
                print("Keeping old csv file without adding existing direct cat-text:")
                direct_cat_text_csv_path = prev_direct_cat_text_csv_path  # Return info

            if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
                print("Postgres DB Single saving label-category data in data base:")
                pgs_conn = PostgresConnection()
                async with PostgresSession(async_engine=pgs_conn.engine,
                                           log_good_ops=log_pgs_good_ops
                                           ) as pgs_session:
                    creation_reason = (
                        f"category-text added: "
                        f"{update_category} - {update_text[:15]}, "
                        f"new dataset: {new_dataset_name}")

                    customer_id = await find_create_customer_qry(
                        ongoing_session=pgs_session,
                        account_username=account_data.account_username,
                        account_id=account_data.account_id,
                        creation_reason=creation_reason)

                    dataset_id = await find_create_dataset_qry(
                        ongoing_session=pgs_session,
                        dataset_name=new_dataset_name,
                        customer_id=customer_id,
                        dataset_csv_dir=new_dataset_dir_path,
                        creation_reason=creation_reason)

                    await cache_unique_lab_cat_dict_qry(
                        ongoing_session=pgs_session,
                        dataset_id=dataset_id,
                        label_category_dict=new_lab_cat_dict,
                        creation_reason=creation_reason,
                        save_only_unique=True)
                    print(f"Postgres DB label-category data saved [OK]:\n"
                          f"new_lab_cat_dict: {new_lab_cat_dict}\n")

                    await save_unique_text_lab_dict_qry(
                        ongoing_session=pgs_session,
                        text_label_dict=new_text_lab_dict,
                        creation_reason=creation_reason,
                        save_only_unique=True)
                    print(f"Postgres DB text-category data saved [OK]:\n"
                          f"new_text_lab_dict: {new_text_lab_dict}\n")
        elif category_exists_flag and not text_exists_flag:
            print("Getting existing label index of existing category:")
            existing_lab_cat_index = None
            for cur_label, cur_cat in prev_lab_cat_dict.items():
                if update_category == cur_cat:
                    existing_lab_cat_index = cur_label

            print("Getting next label-category dict with new category:")
            new_lab_cat_dict = {existing_lab_cat_index: update_category}

            print("Creating new text-label dict:")
            new_text_lab_dict = {update_text: existing_lab_cat_index}

            new_category = "category already exists"  # Just return info
            new_text = update_text  # Just return info

            print("Saving existing label-category data into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing lab-cat:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                lab_cat_csv_path = new_lab_cat_csv_path  # Return info
            else:  # Keep old csv file
                print("Keeping old csv file without adding existing lab-cat:")
                lab_cat_csv_path = prev_lab_cat_csv_path  # Return info

            print("Saving new text-label data into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new txt-lab csv file
                print("Copying and creating new csv file with adding new text-lab:")
                os.makedirs(name=new_dataset_dir_path, exist_ok=True)
                new_text_lab_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
                shutil.copy2(src=prev_text_lab_csv_path,
                             dst=new_text_lab_csv_path)
                with open(file=new_text_lab_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_text_lab_csv_f:
                    csv_text_lab = CsvTextLabel(new_text_lab_csv_f)
                    csv_text_lab.add_single_text_label_row(
                        new_text=update_text,
                        new_label=existing_lab_cat_index)
                text_lab_csv_path = new_text_lab_csv_path
            else:  # Append existing txt-lab csv file
                print("Appending old csv file with adding new text-lab:")
                with open(file=prev_text_lab_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_text_lab_csv_f:
                    csv_text_lab = CsvTextLabel(prev_text_lab_csv_f)
                    csv_text_lab.add_single_text_label_row(
                        new_text=update_text,
                        new_label=existing_lab_cat_index)
                text_lab_csv_path = prev_text_lab_csv_path

            print("Saving existing direct category-text into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing direct cat-text:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_direct_cat_text_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME)
                shutil.copy2(src=prev_direct_cat_text_csv_path,
                             dst=new_direct_cat_text_csv_path)
                direct_cat_text_csv_path = new_direct_cat_text_csv_path  # Return info
            else:  # Keep existing csv file
                print("Keeping old csv file without adding existing lab-cat pair:")
                direct_cat_text_csv_path = prev_direct_cat_text_csv_path  # Return info

            if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
                print("Postgres DB Single saving label-category data in data base:")
                pgs_conn = PostgresConnection()
                async with PostgresSession(async_engine=pgs_conn.engine,
                                           log_good_ops=log_pgs_good_ops
                                           ) as pgs_session:
                    creation_reason = (
                        f"category-text added: "
                        f"{update_category} - {update_text[:15]}, "
                        f"new dataset: {new_dataset_name}")

                    customer_id = await find_create_customer_qry(
                        ongoing_session=pgs_session,
                        account_username=account_data.account_username,
                        account_id=account_data.account_id,
                        creation_reason=creation_reason)

                    dataset_id = await find_create_dataset_qry(
                        ongoing_session=pgs_session,
                        dataset_name=new_dataset_name,
                        customer_id=customer_id,
                        dataset_csv_dir=new_dataset_dir_path,
                        creation_reason=creation_reason)

                    await cache_unique_lab_cat_dict_qry(
                        ongoing_session=pgs_session,
                        dataset_id=dataset_id,
                        label_category_dict=new_lab_cat_dict,
                        creation_reason=creation_reason,
                        save_only_unique=True)
                    print(f"Postgres DB label-category data saved [OK]:\n"
                          f"new_lab_cat_dict: {new_lab_cat_dict}\n")

                    await save_unique_text_lab_dict_qry(
                        ongoing_session=pgs_session,
                        text_label_dict=new_text_lab_dict,
                        creation_reason=creation_reason,
                        save_only_unique=True)
                    print(f"Postgres DB text-category data saved [OK]:\n"
                          f"new_text_lab_dict: {new_text_lab_dict}\n")
        elif text_exists_flag and not category_exists_flag:
            new_category = update_category  # Just return info
            new_text = f"direct predict text: {update_text}"  # Just return info

            print("Saving existing label-category data into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing lab-cat:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                lab_cat_csv_path = new_lab_cat_csv_path  # Return info
            else:  # Keep old csv file
                print("Keeping old csv file without adding existing label-category:")
                lab_cat_csv_path = prev_lab_cat_csv_path  # Return info

            print("Saving existing text-label data into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing text-label:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_text_lab_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
                shutil.copy2(src=prev_text_lab_csv_path,
                             dst=new_text_lab_csv_path)
                text_lab_csv_path = new_text_lab_csv_path  # Return info
            else:  # Keep old csv file
                print("Keeping old csv file without adding existing text-label:")
                text_lab_csv_path = prev_text_lab_csv_path  # Return info

            print("Saving new direct category-text into new csv file:")
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new direct cat-text csv file
                print("Copying and creating new csv file with adding new direct cat-text:")
                os.makedirs(name=new_dataset_dir_path, exist_ok=True)
                new_direct_cat_text_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME)
                shutil.copy2(src=prev_direct_cat_text_csv_path,
                             dst=new_direct_cat_text_csv_path)
                with open(file=new_direct_cat_text_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_direct_cat_txt_csvf:
                    csv_direct_cat_text = CsvDirectCategoryText(new_direct_cat_txt_csvf)
                    csv_direct_cat_text.add_single_direct_category_text_row(
                        account_id=account_data.account_id,
                        account_username=account_data.account_username,
                        new_direct_category=update_category,
                        new_direct_text=update_text)
                    direct_cat_text_csv_path = new_direct_cat_text_csv_path
            else:  # Append existing category-text csv file
                print("Appending old csv file with adding new direct cat-text:")
                with open(file=prev_direct_cat_text_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_direct_cat_txt_csvf:
                    direct_cat_text = CsvDirectCategoryText(prev_direct_cat_txt_csvf)
                    direct_cat_text.add_single_direct_category_text_row(
                        account_id=account_data.account_id,
                        account_username=account_data.account_username,
                        new_direct_category=update_category,
                        new_direct_text=update_text)
                direct_cat_text_csv_path = prev_text_lab_csv_path

            if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
                print("Postgres DB Single saving label-category data in data base:")
                pgs_conn = PostgresConnection()
                async with PostgresSession(async_engine=pgs_conn.engine,
                                           log_good_ops=log_pgs_good_ops
                                           ) as pgs_session:
                    creation_reason = (
                        f"category-text added: "
                        f"{update_category} - {update_text[:15]}, "
                        f"new dataset: {new_dataset_name}")

                    customer_id = await find_create_customer_qry(
                        ongoing_session=pgs_session,
                        account_username=account_data.account_username,
                        account_id=account_data.account_id,
                        creation_reason=creation_reason)

                    await find_create_dataset_qry(  # Returns dataset_id
                        ongoing_session=pgs_session,
                        dataset_name=new_dataset_name,
                        customer_id=customer_id,
                        dataset_csv_dir=new_dataset_dir_path,
                        creation_reason=creation_reason)

                    direct_predict_new_data = {
                        "account_id": account_data.account_id,
                        "account_username": account_data.account_username,
                        "direct_category": update_category,
                        "direct_text": update_text}
                    direct_predict_dicts_list = [direct_predict_new_data, ]
                    await save_direct_cat_text_list_qry(
                        ongoing_session=pgs_session,
                        direct_cat_text_dicts_list=direct_predict_dicts_list,
                        creation_reason=creation_reason,
                        save_only_unique=True)
                    print(f"Postgres DB text-category data saved [OK]:\n"
                          f"direct_category: {update_category}\n"
                          f"creation_reason: {update_text}\n")

        print("Saving updated dataset ini file path:")
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

        new_csv_files_data = {
            "lab_cat_csv_path": lab_cat_csv_path,
            "text_lab_csv_path": text_lab_csv_path,
            "direct_cat_text_csv_path": direct_cat_text_csv_path,
            "last_saved_dataset_ini_fpath": last_saved_dataset_ini_fpath,
            "new_category": new_category,
            "new_text": new_text}
        return new_csv_files_data
    except Exception as error:
        log_text = (f"BERT add and save single text-category pair [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
