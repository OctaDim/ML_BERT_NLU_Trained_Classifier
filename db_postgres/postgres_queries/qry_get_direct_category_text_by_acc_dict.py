from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.direct_predict_model import (
    DirectPredictModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_direct_categ_text_by_acc_dict_qry(
        ongoing_session: AsyncSession,
        account_id: str = None,
        account_username: str = None,
        reversed_direct_text_cat_dict: bool = False
) -> Dict[str, str]:
    filter_fields = {"account_id": account_id,
                     "account_username": account_username,
                     "active": True}
    pgs_direct_cat_text_objs = await get_model_rows_flex_query(
        orm_model_class=DirectPredictModel,
        ongoing_session=ongoing_session,
        selected_fields=["direct_category", "direct_text"],
        fields_values_filter=filter_fields,
        order_by_fields=DirectPredictModel.created_at,
        return_scalars=False)
    print(f"####### type(pgs_direct_cat_text_objs): {type(pgs_direct_cat_text_objs)}")
    print(f"####### len(pgs_direct_cat_text_objs): {len(pgs_direct_cat_text_objs)}")
    # print(f"####### pgs_direct_cat_text_objs: {pgs_direct_cat_text_objs}")  # Too long

    pgs_direct_cat_text_cat_dict = {}
    for cur_record in pgs_direct_cat_text_objs:
        direct_category = cur_record.direct_category
        direct_text = cur_record.direct_text
        if reversed_direct_text_cat_dict:
            pgs_direct_cat_text_cat_dict[direct_text] = direct_category
        else:
            pgs_direct_cat_text_cat_dict[direct_category] = direct_text
    return pgs_direct_cat_text_cat_dict


if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_async_conn.pgs_async_connection import (
        PostgresConnection)
    from db_postgres.postgres_async_conn.postgres_async_session import (
        PostgresSession)


    async def test_get_direct_category_text_by_acc_dict_qry():
        account_id = "30"
        account_username = "globalhome"

        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
            pgs_direct_cat_dict = await get_direct_categ_text_by_acc_dict_qry(
                ongoing_session=pgs_session,
                account_id=account_id,
                account_username=account_username,
                reversed_direct_text_cat_dict=True
            )

        print(pgs_direct_cat_dict)

    asyncio.run(
        main=test_get_direct_category_text_by_acc_dict_qry(),
        debug=True)
