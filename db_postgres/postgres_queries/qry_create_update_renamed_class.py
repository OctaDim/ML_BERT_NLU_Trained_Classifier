from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db_postgres.postgres_models.renamed_class_model import (
    RenamedCustomerClassModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from db_postgres.postgres_queries_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def create_update_renamed_class_qry(
        ongoing_session: AsyncSession,
        customer_id: int,
        label_category_id: int,
        renamed_class_name: str,
        creation_reason: str
) -> int | None:
    filter_fields = {"customer_id": customer_id,
                     "label_category_id": label_category_id}

    renamed_classes_objs = await get_model_rows_flex_query(
        orm_model_class=RenamedCustomerClassModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=filter_fields,
        order_by_fields=None,
        return_scalars=True)

    renamed_class_new_data = {"customer_id": customer_id,
                              "label_category_id": label_category_id,
                              "renamed_class_name": renamed_class_name,
                              "creation_reason": creation_reason}
    try:
        if renamed_classes_objs:
            found_renamed_class_obj = renamed_classes_objs[0]
            found_renamed_class_id = found_renamed_class_obj.id
            renamed_class_new_data.update({"id": found_renamed_class_id})  # To update record if that pk exists else new

        renamed_class_obj = RenamedCustomerClassModel()
        await merge_obj_to_ongoing_session(
            ongoing_session=ongoing_session,
            object_to_merge=renamed_class_obj,
            new_update_data=renamed_class_new_data)
        await ongoing_session.flush()
        renamed_class_id = renamed_class_obj.id
        return renamed_class_id
    except Exception as error:
        log_text = (f"Finding or creating renamed class [ERROR]: "
                    f"error: {error}, "
                    f"orm_model_class: {RenamedCustomerClassModel}, "
                    f"filter_fields: {filter_fields}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
