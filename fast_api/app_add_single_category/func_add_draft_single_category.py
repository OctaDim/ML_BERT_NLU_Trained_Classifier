from fastapi import HTTPException, status

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.enums import DRAFT_STATUS
from configs.settings import (
    BERT_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_conn_async.pgs_async_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn_async.postgres_async_session import (
    PgsAsyncSession)
from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_get_draft_category_list import (
    get_draft_category_list_qry)
from db_postgres.postgres_queries.qry_get_label_category_dict import (
    get_label_category_dict_qry)
from db_postgres.postgres_queries.qry_save_new_model_data import (
    save_new_model_data_qry)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import (
    CsvLabelCategory)
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)


async def add_draft_single_category(
        account_data: AccountDataBert,
        update_category: str,
        bert_model_inst: ClassifierBERT
) -> dict:
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    print("DB Postgres Getting current category-label dictionary:")
    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=log_pgs_good_ops
                               ) as pgs_session:
        pgs_cat_lab_dict = await get_label_category_dict_qry(
            ongoing_session=pgs_session,
            reversed_category_label_dict=True)

    if not pgs_cat_lab_dict:
        if bert_model_inst.last_saved_dataset_dir:
            cur_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
        else:
            last_saved_dataset_dir = get_last_saved_dataset_dir_path()
            if last_saved_dataset_dir:
                cur_dataset_dir_path = last_saved_dataset_dir
            else:
                initial_dataset_dir = get_initial_dataset_dir_path()
                if initial_dataset_dir:
                    cur_dataset_dir_path = initial_dataset_dir
                else:
                    cur_dataset_dir_path = ""

        print("Getting current label-category csv path:")
        cur_lab_cat_csv_path = None
        try:
            cur_lab_cat_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[cur_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

            print("Getting current category-label dictionary from csv file:")
            with open(file=cur_lab_cat_csv_path,
                      mode="r", encoding="utf-8") as prev_lab_cat_csv_f:
                csf_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
                cur_cat_lab_csv_dict = csf_lab_cat.get_label_category_dict(
                    reversed_category_label=True)
            print(f"cur_cat_lab_csv_dict: {cur_cat_lab_csv_dict}")  # Too long
            print(f"type(cur_cat_lab_csv_dict): {type(cur_cat_lab_csv_dict)}")
            print(f"len(cur_cat_lab_csv_dict): {len(cur_cat_lab_csv_dict)}")

            if not cur_cat_lab_csv_dict:
                error_log = (
                    f"Empty or wrong label-category csv data [ERROR]:\n"
                    f"cur_lab_cat_csv_path: {cur_lab_cat_csv_path}\n"
                    f"cur_cat_lab_csv_dict: {cur_cat_lab_csv_dict}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            cur_cat_lab_dict = cur_cat_lab_csv_dict
        except Exception as lab_cat_csv_file_error:
            error_log = (
                f"Getting label-category csv file data [ERROR]:\n"
                f"error: {lab_cat_csv_file_error}\n"
                f"cur_lab_cat_csv_path: {cur_lab_cat_csv_path}\n"
                f"cur_cat_lab_csv_dict: {cur_cat_lab_csv_dict}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)
    else:  # if pgs_cat_lab_dict: Postgres DB category-label data exists
        cur_cat_lab_dict = pgs_cat_lab_dict

    try:
        print("DB Postgres Getting current draft categories list:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            draft_categories_list = await get_draft_category_list_qry(
                ongoing_session=pgs_session)

        print("Checking single category already exists in dataset or in drafts:")
        if update_category in cur_cat_lab_dict:
            dataset_existing_cat = update_category
            new_draft_cat_info = f"exists in dataset: {update_category}"  # Just return info
            current_status = DRAFT_STATUS.DATASET_EXISTS
            active_val = False
            creation_reason = (f"single cat: {update_category}, "
                               f"active: {active_val}, "
                               f"new draft category: {new_draft_cat_info}")
        elif update_category in draft_categories_list:
            dataset_existing_cat = None
            new_draft_cat_info = f"exists in drafts: {update_category}"  # Just return info
            current_status = DRAFT_STATUS.DRAFT_EXISTS
            active_val = False
            creation_reason = (f"single cat: {update_category}, "
                               f"active: {active_val}, "
                               f"new draft category: {new_draft_cat_info}")
        else:
            dataset_existing_cat = None
            new_draft_cat_info = f"new draft category: {update_category}"  # Just return info
            current_status = DRAFT_STATUS.NEW_CLASS_DRAFT_ADDED
            active_val = True
            creation_reason = (f"single cat: {update_category}, "
                               f"active: {active_val}, "
                               f"new draft category: {new_draft_cat_info}")
        print("DB Postgres Saving single category to draft db data:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            customer_id = await find_create_customer_qry(
                ongoing_session=pgs_session,
                account_username=account_data.account_username,
                account_id=account_data.account_id,
                creation_reason=creation_reason)

            new_draft_data = {
                "customer_id": customer_id,
                "account_id": account_data.account_id,
                "account_username": account_data.account_username,
                "ds_existing_category": dataset_existing_cat,
                "draft_category": update_category,
                "current_status": current_status,
                "active": active_val,
                "creation_reason": creation_reason}

            await save_new_model_data_qry(
                ModelClassORM=DraftCategoryTextModel,
                ongoing_session=pgs_session,
                new_data=new_draft_data)
            print(f"DB Postgres single category saved as draft [OK]:\n"
                  f"new_draft_cat_info: {new_draft_cat_info}\n")

        common_csv_f_note = "db draft table used instead of dataset"
        new_csv_files_data = {
            "lab_cat_csv_path": common_csv_f_note,
            "text_lab_csv_path": common_csv_f_note,
            "direct_cat_text_csv_path": common_csv_f_note,
            "last_saved_dataset_ini_fpath": common_csv_f_note,
            "new_category": new_draft_cat_info}
        return new_csv_files_data
    except Exception as error:
        error_log = (f"BERT save single category as database draft [ERROR]: "
                     f"error: {error}")
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_log)
