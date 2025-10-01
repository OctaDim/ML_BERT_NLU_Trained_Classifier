from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_label_idx_and_id_dict_qry(
        ongoing_session: AsyncSession
) -> Dict[int, int]:
    pgs_lab_cat_objs = await get_model_rows_flex_query(
        orm_model_class=LabelCategoryModel,
        ongoing_session=ongoing_session,
        selected_fields=["id", "label_index"],
        fields_values_filter=None,
        order_by_fields=LabelCategoryModel.label_index,
        return_scalars=False)
    print(f"####### type(pgs_lab_cat_objs): {type(pgs_lab_cat_objs)}")
    print(f"####### len(pgs_lab_cat_objs): {len(pgs_lab_cat_objs)}")
    print(f"####### pgs_lab_cat_objs: {pgs_lab_cat_objs}")

    pgs_lab_idx_and_id_dict = {}
    for cur_record in pgs_lab_cat_objs:
        label_index = cur_record.label_index
        label_id = cur_record.id
        pgs_lab_idx_and_id_dict[label_index] = label_id
    return pgs_lab_idx_and_id_dict
