from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_models.label_text_model import LabelTextModel
from db_postgres.postgres_queries.get_model_records_flex_query import (
    get_model_rows_flex_query)
from db_postgres.postgres_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_label_text_dict_qry(
        ongoing_session: AsyncSession,
        label_text_dict: Dict[int, str]
) -> None:
    label_category_obj_id, cur_label_index, cur_text = None, None, None
    try:
        new_lab_text_model_obj = LabelTextModel()
        for cur_text, cur_label_index in label_text_dict.items():
            label_category_objs = await get_model_rows_flex_query(
                orm_model_class=LabelCategoryModel,
                ongoing_session=ongoing_session,
                selected_fields=None,
                fields_values_filter={"label_index": cur_label_index},
                order_by_fields=None,
                return_scalars=True)
            label_category_obj_id = label_category_objs[0].id

            label_text_new_data = {
                "label_category_id": label_category_obj_id,
                "label_index_hint": cur_label_index,
                "text": cur_text}
            await merge_obj_to_ongoing_session(
                object_to_merge=new_lab_text_model_obj,
                ongoing_session=ongoing_session,
                new_update_data=label_text_new_data)
        print(f"DB Postgres saving label-text data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving label-text data [ERROR]: "
                     f"error: {error}\n"
                     f"label_category_obj_id: {label_category_obj_id}\n"
                     f"cur_label_index: {cur_label_index}\n"
                     f"cur_text: {cur_text}\n"
                     f"label_text_dict: {label_text_dict}\n")
        print(error_log)
        raise
