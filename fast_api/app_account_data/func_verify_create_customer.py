from fastapi import HTTPException
from starlette import status

from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import PostgresSession
from db_postgres.postgres_models.customer_model import CustomerModel
from db_postgres.postgres_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from db_postgres.postgres_utils.model_object_attrs_update import (
    update_model_obj_no_commit)


async def verify_create_customer(account_username: str,
                                 account_id: str) -> int | None:
    if not account_username or not account_id:
        return None

    fields_filter = {"account_username": account_username,
                     "account_id": account_id}

    pgs_conn = PostgresConnection()
    async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
        customer_obj = await get_model_rows_flex_query(
            orm_model_class=CustomerModel,
            ongoing_session=pgs_session,
            fields_values_filter=fields_filter,
            order_by_fields=None)

        try:
            exist_customer_id = customer_obj[0].id if customer_obj else None
            if exist_customer_id:
                return exist_customer_id

            new_customer_obj = CustomerModel()
            customer_update_data = {"account_username": account_username,
                                    "account_id": account_id}
            update_model_obj_no_commit(orm_model_object=new_customer_obj,
                                       new_update_data=customer_update_data)
            pgs_session.add(new_customer_obj)
            await pgs_session.flush()
            new_customer_id = new_customer_obj.id
            return new_customer_id
        except Exception as error:
            log_text = (f"Verifying or creating customer data [ERROR]:\n"
                        f"error: {error}\n"
                        f"orm_model_class: {CustomerModel}\n"
                        f"fields_filter: {fields_filter}\n"
                        f"order_by_fields: {None}\n")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=log_text)
