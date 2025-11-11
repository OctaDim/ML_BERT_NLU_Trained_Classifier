# ####################### DEBUG CODE (start) ###########################
# ######################################################################


async def get_records():
    from db_postgres.postgres_conn_async.pgs_async_connection import (
        PgsAsyncConnection)
    from db_postgres.postgres_conn_async.postgres_async_session import (
        PgsAsyncSession)
    from db_postgres.postgres_models.label_category_model import (
        LabelCategoryModel)
    from db_postgres.postgres_queries_utils.convert_orm_rows_to_dict import (
        convert_model_recs_to_dicts)
    from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
        get_model_rows_flex_query)

    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
        print(pgs_session)
        pgs_lab_cat_recs = await get_model_rows_flex_query(
            orm_model_class=LabelCategoryModel,
            ongoing_session=pgs_session,
            fields_values_filter=None,
            order_by_fields=None,
            return_scalars=True)  # If is false use only inside context manager
        pgs_lab_cat_dicts_2 = await convert_model_recs_to_dicts(
            model_records_list=pgs_lab_cat_recs)
        print(f"####### pgs_lab_cat_dicts_2 [{len(pgs_lab_cat_dicts_2)}] => {pgs_lab_cat_dicts_2}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main=get_records(), debug=True)

# ########################## DEBUG CODE (end) ##########################
# ######################################################################
