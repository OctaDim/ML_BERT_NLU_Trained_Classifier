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
from db_postgres.postgres_queries.qry_get_label_category_dict import (
    get_label_category_dict_qry)
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


async def add_save_single_category(
        update_category: str,
        bert_model_inst: ClassifierBERT
) -> dict:
    if ALCHEMY_OPTIONS.USE_POSTGRES_DATA_BASE:
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
            pgs_prev_lab_cat_dict = await get_label_category_dict_qry(pgs_session)
        print(f"pgs_prev_lab_cat_dict: {pgs_prev_lab_cat_dict}")
        print(f"type(pgs_prev_lab_cat_dict): {type(pgs_prev_lab_cat_dict)}")
        print(f"len(pgs_prev_lab_cat_dict): {len(pgs_prev_lab_cat_dict)}")

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

    prev_lab_cat_csv_path = None
    new_lab_cat_csv_path = None
    try:
        print("\nGetting previous label-category dictionary:")
        prev_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

        with open(file=prev_lab_cat_csv_path,
                  mode="r", encoding="utf-8") as prev_lab_cat_csv_f:
            csf_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
            prev_lab_cat_csv_dict = csf_lab_cat.get_label_category_dict()
        print("type(prev_lab_cat_csv_dict)", type(prev_lab_cat_csv_dict))
        print("prev_lab_cat_csv_dict", prev_lab_cat_csv_dict)

        if not prev_lab_cat_csv_dict:
            log_text = (f"Empty or wrong label-category csv data [ERROR]: "
                        f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}, "
                        f"prev_lab_cat_dict: {prev_lab_cat_csv_dict}\n")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)
        # prev_lab_cat_dict = prev_lab_cat_csv_dict
    except Exception as lab_cat_csv_file_error:
        error_log = (f"Getting label-category csv file data [ERROR]: "
                     f"error: {lab_cat_csv_file_error}\n"
                     f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}\n"
                     f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}\n")
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_log)

    if pgs_prev_lab_cat_dict:  # Label-category data exists in Postgres DB
        prev_lab_cat_dict = pgs_prev_lab_cat_dict
    elif prev_lab_cat_csv_dict:
        prev_lab_cat_dict = prev_lab_cat_csv_dict
    else:
        prev_lab_cat_dict = {}

    print("Single adding one label-category pair for single category:")
    if update_category not in prev_lab_cat_dict.values():
        next_label_new_index = max(prev_lab_cat_dict.keys()) + 1
        prev_lab_cat_dict[next_label_new_index] = update_category
        new_category = update_category
    else:
        next_label_new_index = None
        new_category = ""

    print("Single adding one single text-label pair for single category:")
    # cur_label = None
    if not next_label_new_index:  # Update category already exists in label-category data
        reversed_lab_cat_dict = {cat: lab for lab, cat in prev_lab_cat_dict}
        cur_label = reversed_lab_cat_dict[update_category]
    else:  # Update category and new label index are new
        cur_label = next_label_new_index

    if ALCHEMY_OPTIONS.USE_POSTGRES_DATA_BASE:
        pass


    try:
        print("Creating new, updating or copying the same label-category csv file:")
        new_dataset_dir_path = get_new_dataset_dir_path()
        if next_label_new_index:  # Update category is new category, not existing in label-category data
            print("Updating existing csv file with new single label-category pair:")
            if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_lab_cat_csv_path = prev_lab_cat_csv_path
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_lab_cat_csv_f:
                    csv_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
                    csv_lab_cat.add_single_label_category_row(
                        new_label=cur_label,
                        new_category=update_category)
            else:
                print("Creating new csv file with new single label-category pair:")
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
                        new_label=cur_label,
                        new_category=update_category)
        else:
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                print("Creating new csv file without adding single label-category pair:")
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
            else:
                print("Keeping old csv file without adding existing label-category pair")

        print("Getting previous text-label csv path:")
        prev_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

        print("Single saving one text-label pair updated csv file:")
        if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
            new_text_lab_csv_path = prev_text_lab_csv_path
            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)
        else:
            os.makedirs(name=new_dataset_dir_path, exist_ok=True)
            new_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)

        bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path

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

        new_csv_files_data = {
            "lab_cat_csv_path": new_lab_cat_csv_path,
            "text_lab_csv_path": new_text_lab_csv_path,
            "last_saved_dataset_ini_fpath": last_saved_dataset_ini_fpath,
            "new_category": new_category}
        return new_csv_files_data
    except Exception as error:
        log_text = (f"BERT add and save single label-category pair [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)


if __name__ == "__main__":
    async def test_main_process():
        from db_postgres.postgres_dependencies.dep_get_bert_model_instance import get_bert_model_instance_dep
        from ML_BERT_classifier.init_bert import init_and_start_bert_model
        from db_postgres.postgres_init.db_tables_initialization import initialize_db_tables

        await initialize_db_tables()
        await init_and_start_bert_model()

        bert_model_inst = await get_bert_model_instance_dep()
        update_category = "new test single category - 111"
        await add_save_single_category(update_category=update_category,
                                       bert_model_inst=bert_model_inst)


    import asyncio

    asyncio.run(main=test_main_process(), debug=True)
