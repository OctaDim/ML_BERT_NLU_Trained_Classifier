from typing import Union, Optional, Tuple, List, Type

from fastapi import HTTPException
from sqlalchemy import select, UnaryExpression
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from starlette import status

from configs.settings import ALCHEMY_OPTIONS
from db_postgres.postgres_utils.create_order_by_partial_query import (
    create_order_for_partial_query)
from db_postgres.postgres_utils.create_where_partial_query import (
    create_where_for_partial_query)
from utils_common.exec_time_decorator import execution_time_decorator


@execution_time_decorator(in_seconds=True,
                          note="Trained models query",
                          exec_time_logging=ALCHEMY_OPTIONS.ALCHEMY_QUERY_EXEC_TIME_LOGS)
async def get_model_objs_flex_query(
        orm_model_class: Type[DeclarativeBase],
        ongoing_session: AsyncSession,
        fields_values_filter: dict = None,
        order_by_fields: Optional[Union[str, Tuple[str, ...],
        UnaryExpression, Tuple[UnaryExpression, ...], None]] = (
                "some_model_field", "some_model_obj.field",)
) -> List[Type[DeclarativeBase]]:
    orm_query = select(orm_model_class)

    try:
        # Creating filter flex query part
        if fields_values_filter:
            orm_query = create_where_for_partial_query(
                orm_model_class=orm_model_class,
                prior_orm_query=orm_query,
                fields_values_filter=fields_values_filter)

        # Creating order flex query part
        if order_by_fields:
            orm_query = create_order_for_partial_query(
                orm_model_class=orm_model_class,
                prior_orm_query=orm_query,
                order_by_fields=order_by_fields)

        result = await ongoing_session.execute(orm_query)
        model_records = list(result.scalars().all())
        return model_records
    except Exception as error:
        log_text = (f"Getting model objs flex query [ERROR]: \n"
                    f"error: {error}\n"
                    f"orm_model_class: {orm_model_class}\n"
                    f"fields_values_filter: {fields_values_filter}\n"
                    f"order_by_fields: {order_by_fields}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=log_text)
