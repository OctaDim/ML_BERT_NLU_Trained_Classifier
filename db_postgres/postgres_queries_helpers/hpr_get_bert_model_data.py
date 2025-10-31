from typing import Dict

from configs.settings import ALCHEMY_OPTIONS
from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_queries.qry_get_direct_category_text_dicts_list import (
    get_direct_cat_text_dicts_list_qry)
from db_postgres.postgres_queries.qry_get_label_category_dict import (
    get_label_category_dict_qry)
from db_postgres.postgres_queries.qry_get_label_text_dict import (
    get_label_text_dict_qry)
from db_postgres.postgres_queries.qry_get_label_text_dicts_list import (
    get_label_text_dicts_list_qry)
from db_postgres.postgres_queries.qry_get_last_dataset_name_and_dir import (
    get_last_dataset_name_and_dir_qry)
from db_postgres.postgres_queries.qry_get_last_saved_model_dir import (
    get_last_saved_model_dir_qry)


async def get_postgres_bert_model_data_hpr() -> Dict[str, any]:
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS
    pgs_conn = PostgresConnection()
    async with PostgresSession(async_engine=pgs_conn.engine,
                               log_good_ops=log_pgs_good_ops
                               ) as pgs_session:
        print("DB Postgres Getting labels-categories data:")
        pgs_lab_cat_dict = await get_label_category_dict_qry(
            ongoing_session=pgs_session,
            reversed_category_label_dict=False)
        print(f"pgs_lab_cat_dict: {pgs_lab_cat_dict}")  # Too long
        print(f"len(pgs_lab_cat_dict): {len(pgs_lab_cat_dict)}")

        print("DB Postgres Getting texts-labels dict data:")
        pgs_text_lab_dict = await get_label_text_dict_qry(
            ongoing_session=pgs_session,
            reversed_text_label_dict=True)
        # print(f"pgs_text_lab_dict: {pgs_text_lab_dict}")  # Too long
        print(f"len(pgs_text_lab_dict): {len(pgs_text_lab_dict)}")

        print("DB Postgres Getting labels-texts dicts list data:")
        pgs_lab_text_dicts_list = await get_label_text_dicts_list_qry(
            ongoing_session=pgs_session)
        # print(f"pgs_lab_text_dicts_list: {pgs_lab_text_dicts_list}")  # Too long
        print(f"len(pgs_lab_text_dicts_list): {len(pgs_lab_text_dicts_list)}")

        print("DB Postgres Getting direct categories-texts dicts list data:")
        pgs_direct_cat_text_dicts_list = await get_direct_cat_text_dicts_list_qry(
            ongoing_session=pgs_session)
        # print(f"pgs_direct_cat_text_dicts_list: {pgs_direct_cat_text_dicts_list}")  # Too long
        print(f"len(pgs_direct_cat_text_dicts_list): {len(pgs_direct_cat_text_dicts_list)}")

        print("DB Postgres Getting last dataset name and directory data:")
        pgs_dataset_data = await get_last_dataset_name_and_dir_qry(
            ongoing_session=pgs_session)
        pgs_dataset_name = pgs_dataset_data[0] if pgs_dataset_data else None
        pgs_dataset_dir = pgs_dataset_data[1] if pgs_dataset_data else None
        print(f"pgs_dataset_name: {pgs_dataset_name}")
        print(f"pgs_dataset_dir: {pgs_dataset_dir}")

        print("DB Postgres Getting last saved BERT model directory path:")
        pgs_model_dir_path = await get_last_saved_model_dir_qry(
            ongoing_session=pgs_session)
        print(f"pgs_model_dir_path: {pgs_model_dir_path}")

        pgs_all_data_flag = all([pgs_lab_cat_dict,
                                 pgs_text_lab_dict,
                                 pgs_dataset_data,
                                 pgs_model_dir_path])
        print(f"pgs_all_data_exists_flag: {pgs_all_data_flag}")

        pgs_bert_model_data = {
            "lab_cat_dict": pgs_lab_cat_dict,
            "text_lab_dict": pgs_text_lab_dict,
            "lab_text_dicts_list": pgs_lab_text_dicts_list,
            "direct_cat_text_dicts_list": pgs_direct_cat_text_dicts_list,
            "dataset_name": pgs_dataset_name,
            "dataset_dir": pgs_dataset_dir,
            "model_dir_path": pgs_model_dir_path,
            "all_data_flag": pgs_all_data_flag}
        return pgs_bert_model_data
