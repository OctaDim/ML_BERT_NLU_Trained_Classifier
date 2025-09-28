from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_label_category_dict_qry(
        ongoing_session: AsyncSession
) -> Dict[int, str]:
    pgs_lab_cat_objs = await get_model_rows_flex_query(
        orm_model_class=LabelCategoryModel,
        ongoing_session=ongoing_session,
        selected_fields=["label_index", "category_name"],
        fields_values_filter=None,
        order_by_fields=LabelCategoryModel.label_index,
        return_scalars=False)
    print(f"####### type(pgs_lab_cat_objs): {type(pgs_lab_cat_objs)}")
    print(f"####### len(pgs_lab_cat_objs): {len(pgs_lab_cat_objs)}")
    # print(f"####### pgs_lab_cat_objs: {pgs_lab_cat_objs}")

    pgs_lab_cat_dict = {}
    for cur_record in pgs_lab_cat_objs:
        label_index = cur_record.label_index
        category_name = cur_record.category_name
        pgs_lab_cat_dict[label_index] = category_name
    return pgs_lab_cat_dict


if __name__ == "__main__":
    import asyncio

    pgs_conn = PostgresConnection()
    asyncio.run(
        main=get_label_category_dict_qry(ongoing_session=pgs_conn.engine),
        debug=True)
