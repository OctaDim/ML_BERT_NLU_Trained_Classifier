async def test_get_model_records_via_flex_query():
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    from db_postgres.postgres_queries.query_all_trained_models import (
        get_model_records_flex_query)
    from db_postgres.postgres_models.customer_model import CustomerModel
    from db_postgres.postgres_async_conn.pgs_async_connection import PostgresConnection

    pgs_conn = PostgresConnection()
    async with pgs_conn.async_session() as pgs_session:
        fields_values_filter = {
            "username": ["Dima-2", "Dima-1"]
            # "username": ["Dima-5", "Dima-10"]
        }

        order_by_fields = ("username", "account_id")

        records = await get_model_records_flex_query(
            orm_model_class=CustomerModel,
            ongoing_session=pgs_session,
            fields_values_filter=fields_values_filter,
            order_by_fields=order_by_fields)

    print(f"records: {records}")
    print(f"type(records): {type(records)}")
    print(f"len(records): {len(records)}")

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    for record in records:
        for field_name, field_value in record.__dict__.items():
            if not field_name.startswith("_"):
                print(f"{field_name} = {field_value}")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main=test_get_model_records_via_flex_query(), debug=True)
