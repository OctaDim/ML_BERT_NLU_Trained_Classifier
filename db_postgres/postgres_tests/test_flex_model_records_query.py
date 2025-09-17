# ####################### DEBUG CODE (start) ###########################
# ######################################################################


async def test_get_model_records_via_flex_query():
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    from db_postgres.postgres_async_conn.pgs_async_connection import PostgresConnection
    from db_postgres.postgres_models.label_category_model import LabelCategoryModel
    # from db_postgres.postgres_models.customer_model import CustomerModel
    from db_postgres.postgres_utils.get_model_records_flex_query import get_model_rows_flex_query

    pgs_conn = PostgresConnection()
    async with pgs_conn.async_session() as pgs_session:
        fields_values_filter = {
            "label_index": [0, 1]
            # "username": ["Dima-5", "Dima-10"]
        }
        fields_values_filter = None

        order_by_fields = ("category_name", )
        order_by_fields = ("username", "account_id")
        order_by_fields = None


        records = await get_model_rows_flex_query(
            orm_model_class=LabelCategoryModel,
            # orm_model_class=CustomerModel,
            ongoing_session=pgs_session,
            fields_values_filter=fields_values_filter,
            order_by_fields=order_by_fields)

    print(f"records: {records}")
    print(f"type(records): {type(records)}")
    print(f"len(records): {len(records)}")

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    for record in records:
        record = record[0]
        for field_name, field_value in record.__dict__.items():
            if not field_name.startswith("_"):
                print(f"{field_name} = {field_value}")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main=test_get_model_records_via_flex_query(), debug=True)
