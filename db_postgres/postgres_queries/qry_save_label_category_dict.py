from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_label_category_data_qry(
        ongoing_session: AsyncSession,
        dataset_id: int,
        label_category_dict: Dict[int, str]
) -> None:
    try:
        new_lab_cat_model_obj = LabelCategoryModel()
        for cur_lab, cur_cat in label_category_dict.items():
            lab_cat_update_data = {
                "label_index": cur_lab,
                "dataset_id": dataset_id,
                "category_name": cur_cat}
            await merge_obj_to_ongoing_session(
                object_to_merge=new_lab_cat_model_obj,
                ongoing_session=ongoing_session,
                new_update_data=lab_cat_update_data)
        print(f"DB Postgres saving label-category data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving label-category data [ERROR]: "
                     f"error: {error}\n"
                     f"dataset_id: {dataset_id}\n"
                     f"label_category_dict: {label_category_dict}\n")
        print(error_log)
        raise
