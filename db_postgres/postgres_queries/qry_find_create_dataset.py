from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db_postgres.postgres_models.dataset_model import DatasetModel
from db_postgres.postgres_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from db_postgres.postgres_utils.model_object_attrs_update import (
    update_model_obj_no_commit)


async def find_create_dataset_qry(
        ongoing_session: AsyncSession,
        dataset_name: str
) -> int | None:
    if not dataset_name:
        return None

    filter_fields = {"dataset_name": dataset_name}
    dataset_obj = await get_model_rows_flex_query(
        orm_model_class=DatasetModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=filter_fields,
        order_by_fields=None)
    try:
        found_dataset_id = dataset_obj[0].id if dataset_obj else None
        if found_dataset_id:
            return found_dataset_id
        new_dataset_obj = DatasetModel()
        customer_new_data = {"dataset_name": dataset_name}
        update_model_obj_no_commit(orm_model_object=new_dataset_obj,
                                   new_update_data=customer_new_data)
        ongoing_session.add(new_dataset_obj)
        await ongoing_session.flush()
        new_dataset_id = new_dataset_obj.id
        return new_dataset_id
    except Exception as error:
        log_text = (f"Finding or creating dataset data [ERROR]:\n"
                    f"error: {error}\n"
                    f"orm_model_class: {DatasetModel}\n"
                    f"filter_fields: {filter_fields}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
