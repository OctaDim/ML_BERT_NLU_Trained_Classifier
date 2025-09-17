from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_label_category_data():
    pgs_conn = PostgresConnection()
    async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
        label_category_recs = await get_model_rows_flex_query(
            orm_model_class=LabelCategoryModel,
            ongoing_session=pgs_session,
            fields_values_filter=None,
            order_by_fields=None)
        label_category_dict = {}
    if label_category_recs:
        for cur_rec in label_category_recs:
            label_category_dict[cur_rec.label_index] = cur_rec.category_name
    return label_category_dict
