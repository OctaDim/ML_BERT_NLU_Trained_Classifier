from typing import Dict

from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_queries.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_label_category_data_qry() -> Dict[int, str]:
    pgs_conn = PostgresConnection()
    async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
        pgs_lab_cat_objs = await get_model_rows_flex_query(
            orm_model_class=LabelCategoryModel,
            ongoing_session=pgs_session,
            selected_fields=["label_index", "category_name"],
            fields_values_filter=None,
            order_by_fields=LabelCategoryModel.label_index,
            return_scalars=False)
        print(f"####### type(pgs_lab_cat_objs): {type(pgs_lab_cat_objs)}")
        print(f"####### len(pgs_lab_cat_objs): {len(pgs_lab_cat_objs)}")
        # print(f"####### pgs_lab_cat_objs: {pgs_lab_cat_objs}")

    pgs_lab_cat_data = {}
    for cur_record in pgs_lab_cat_objs:
        label_index = cur_record.label_index
        category_name = cur_record.category_name
        pgs_lab_cat_data[label_index] = category_name
    return pgs_lab_cat_data


if __name__ == "__main__":
    import asyncio

    asyncio.run(main=get_label_category_data_qry(), debug=True)
