from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db_postgres.postgres_models.customer_model import CustomerModel
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from db_postgres.postgres_queries_utils.model_object_attrs_update import (
    update_model_obj_no_commit)


async def find_create_customer_qry(
        ongoing_session: AsyncSession,
        account_username: str,
        account_id: str,
        creation_reason: str = None
) -> int | None:
    if not account_username or not account_id:
        return None

    filter_fields = {"account_username": account_username,
                     "account_id": account_id}

    customer_objs = await get_model_rows_flex_query(
        orm_model_class=CustomerModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=filter_fields,
        order_by_fields=None)
    try:
        if customer_objs:
            customer_id_found = customer_objs[0].id
            return customer_id_found

        new_customer_obj = CustomerModel()
        customer_new_data = {"account_username": account_username,
                             "account_id": account_id,
                             "creation_reason": creation_reason}
        update_model_obj_no_commit(orm_model_object=new_customer_obj,
                                   new_update_data=customer_new_data)
        ongoing_session.add(new_customer_obj)
        await ongoing_session.flush()
        new_customer_id = new_customer_obj.id
        return new_customer_id
    except Exception as error:
        log_text = (f"Finding or creating customer data [ERROR]:\n"
                    f"error: {error}\n"
                    f"orm_model_class: {CustomerModel}\n"
                    f"filter_fields: {filter_fields}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
