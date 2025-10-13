# import asyncio
# from functools import partial
import copy
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
from db_postgres.postgres_queries_helpers.hpr_get_bert_model_data import (
    get_postgres_bert_model_data_hpr)
from fast_api.app_account_data.scheme_account_data import AccountDataBert
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


async def add_save_single_category(
        account_data: AccountDataBert,
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
                            f"prev_lab_cat_dict: {prev_lab_cat_csv_dict}\n")
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
            if not prev_text_lab_csv_path:
                error_log = (f"Empty text-label csv file path [ERROR]:\n"
                            f"prev_text_lab_csv_path: {prev_text_lab_csv_path}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
        except Exception as text_lab_csv_file_error:
            error_log = (f"Getting text-label csv file path [ERROR]:\n"
                         f"error: {text_lab_csv_file_error}\n"
                         f"prev_text_lab_csv_path: {prev_text_lab_csv_path}\n")
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

            if not prev_direct_cat_text_csv_path:
                error_log = (
                    f"Empty direct category-text csv path [ERROR]:\n"
                    f"prev_direct_cat_text_csv_path: {prev_direct_cat_text_csv_path}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
        except Exception as text_lab_csv_file_error:
            error_log = (
                f"Getting direct category-text csv path [ERROR]:\n"
                f"error: {text_lab_csv_file_error}\n"
                f"prev_direct_cat_text_csv_path: {prev_direct_cat_text_csv_path}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)
    else:  # All Postgres DB data exists (if pgs_all_data_flag:)
        prev_lab_cat_dict = pgs_bert_model_data["lab_cat_dict"]
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

    try:
        print("Creating new dataset directory path:")
        new_dataset_dir_path = get_new_dataset_dir_path()
        new_dataset_name = new_dataset_dir_path.split(os.path.sep)[-1]

        print("Single saving label-category data in csv file:")
        if update_category not in prev_lab_cat_dict.values():  # New label and category
            print("Getting new label new index for new category:")
            next_label_new_index = max(prev_lab_cat_dict.keys()) + 1
            new_category = update_category  # Return info
            print("Creating new label-category dict:")
            new_lab_cat_dict = copy.copy(prev_lab_cat_dict)
            new_lab_cat_dict[next_label_new_index] = update_category

            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and updating new csv file with new single lab-cat:")
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
            else:  # Overwrite existing csv file
                print("Overwriting existing csv file with new single lab-cat:")
                with open(file=prev_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_lab_cat_csv_f:
                    csv_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
                    csv_lab_cat.add_single_label_category_row(
                        new_label=next_label_new_index,
                        new_category=update_category)
                lab_cat_csv_path = prev_lab_cat_csv_path  # Return info
        else:  # Category already exists
            print("Getting existing lab-cat dict as new lab-cat dict:")
            # reversed_lab_cat_dict = {cat: lab for lab, cat in prev_lab_cat_dict}
            # existing_label = reversed_lab_cat_dict[update_category]
            # next_label_new_index = None
            new_lab_cat_dict = prev_lab_cat_dict
            new_category = "category already exists"  # Just for return info

            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
                print("Copying and creating new csv file without adding existing lab-cat:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                lab_cat_csv_path = new_lab_cat_csv_path  # Return info
            else:  # Overwrite existing csv file
                print("Keeping old csv file without adding existing lab-cat:")
                lab_cat_csv_path = prev_lab_cat_csv_path  # Return info

        print("Single saving text-label data in csv file:")
        if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
            print("Copying and creating new csv file without adding existing text-lab:")
            os.makedirs(name=new_dataset_dir_path, exist_ok=True)
            new_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)
            text_lab_csv_path = new_text_lab_csv_path
        else:  # Overwrite existing csv file
            print("Keeping old csv file without adding existing text-lab:")
            text_lab_csv_path = prev_text_lab_csv_path

        print("Saving existing direct category-text data into new csv file:")
        if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:  # Create new csv file
            print("Copying and creating new csv file without adding existing direct cat-text:")
            os.makedirs(new_dataset_dir_path, exist_ok=True)
            new_direct_cat_text_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)
            shutil.copy2(src=prev_direct_cat_text_csv_path,
                         dst=new_direct_cat_text_csv_path)
            direct_cat_text_csv_path = new_direct_cat_text_csv_path  # Return info
        else:  # Keep old csv file
            print("Keeping old csv file without adding existing direct cat-text:")
            direct_cat_text_csv_path = prev_direct_cat_text_csv_path  # Return info

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

        if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
            print("Postgres DB Single saving label-category data in data base:")
            pgs_conn = PostgresConnection()
            async with PostgresSession(async_engine=pgs_conn.engine,
                                       log_good_ops=log_pgs_good_ops
                                       ) as pgs_session:
                creation_reason = (f"single category added: "
                                   f"{update_category}")

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

        new_csv_files_data = {
            "lab_cat_csv_path": lab_cat_csv_path,
            "text_lab_csv_path": text_lab_csv_path,
            "direct_cat_text_csv_path": direct_cat_text_csv_path,
            "last_saved_dataset_ini_fpath": last_saved_dataset_ini_fpath,
            "new_category": new_category}
        return new_csv_files_data
    except Exception as error:
        error_log = (f"BERT add and save single category [ERROR]: "
                    f"error: {error}")
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_log)


if __name__ == "__main__":
    async def test_main_process():
        from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
            get_bert_model_instance_dep)
        from ML_BERT_classifier.init_bert import init_and_start_bert_model
        from db_postgres.postgres_init.db_tables_initialization import (
            initialize_db_tables)

        await initialize_db_tables()
        await init_and_start_bert_model()

        bert_model_inst = await get_bert_model_instance_dep()
        update_category = "new test single category - 444"
        account_data = AccountDataBert(account_username="globalhome",
                                       account_id="30")
        await add_save_single_category(account_data=account_data,
                                       update_category=update_category,
                                       bert_model_inst=bert_model_inst)


    import asyncio

    asyncio.run(main=test_main_process(), debug=True)
