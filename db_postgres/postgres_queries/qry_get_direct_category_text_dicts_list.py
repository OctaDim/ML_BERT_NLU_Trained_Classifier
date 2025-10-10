from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.direct_predict_model import (
    DirectPredictModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_direct_cat_text_dicts_list_qry(
        ongoing_session: AsyncSession,
) -> List[Dict[str, str]] | None:
    """Returns list of dicts with direct_category (str) and direct_text (str)"""
    pgs_direct_cat_text_objs = await get_model_rows_flex_query(
        orm_model_class=DirectPredictModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=None,
        order_by_fields=None,
        return_scalars=True)
    print(f"####### pgs_direct_cat_text_objs: {pgs_direct_cat_text_objs}")  # Too long
    print(f"####### type(pgs_direct_cat_text_objs): {type(pgs_direct_cat_text_objs)}")
    print(f"####### len(pgs_direct_cat_text_objs): {len(pgs_direct_cat_text_objs)}")

    pgs_direct_cat_text_dicts_list = []
    for cur_record in pgs_direct_cat_text_objs:
        cur_direct_cat_text_dict = {
            "account_id": cur_record.account_id,
            "account_username": cur_record.account_username,
            "direct_category": cur_record.direct_category,
            "direct_text": cur_record.direct_text,
            "creation_reason": cur_record.creation_reason}
        pgs_direct_cat_text_dicts_list.append(cur_direct_cat_text_dict)
    return pgs_direct_cat_text_dicts_list


if __name__ == "__main__":
    from db_postgres.postgres_async_conn.pgs_async_connection import (
        PostgresConnection)
    from db_postgres.postgres_async_conn.postgres_async_session import (
        PostgresSession)
    import asyncio


    async def test_get_label_text_list_qry():
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
            pgs_text_lab_list = await get_direct_cat_text_dicts_list_qry(
                ongoing_session=pgs_session)
            for cur_row in pgs_text_lab_list:
                print(cur_row)


    asyncio.run(main=test_get_label_text_list_qry(), debug=True)
