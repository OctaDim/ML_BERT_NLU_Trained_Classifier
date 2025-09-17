from typing import Dict

from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_pgs_label_category_data(
        label_category_dict: Dict[int, str]
) -> None:
    pgs_conn = PostgresConnection()
    try:
        async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
            new_lab_cat_model_obj = LabelCategoryModel()
            for cur_lab, cur_cat in label_category_dict.items():
                lab_cat_update_data = {
                    "label_index": cur_lab,
                    "category_name": cur_cat}
                await merge_obj_to_ongoing_session(
                    object_to_merge=new_lab_cat_model_obj,
                    ongoing_session=pgs_session,
                    new_update_data=lab_cat_update_data)
    except Exception as error:
        error_log = (f"DB Postgres saving label-category data [ERROR]: \n"
                     f"error: {error} \n"
                     f"label_category_dict: {label_category_dict} \n")
        print(error_log)
        raise
