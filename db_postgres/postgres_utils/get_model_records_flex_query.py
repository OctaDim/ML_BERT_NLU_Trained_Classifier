from typing import Union, Optional, Tuple, Type, Any, Sequence

from sqlalchemy import select, UnaryExpression, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from configs.settings import ALCHEMY_OPTIONS
from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_utils.create_order_by_partial_query import (
    create_order_for_partial_query)
from db_postgres.postgres_utils.create_where_partial_query import (
    create_where_for_partial_query)
from utils_common.exec_time_decorator import execution_time_decorator


@execution_time_decorator(in_seconds=True,
                          note="Get_model_recs_flex_query",
                          exec_time_logging=ALCHEMY_OPTIONS.ALCHEMY_QUERY_EXEC_TIME_LOGS)
async def get_model_rows_flex_query(
        orm_model_class: Type[Base],
        ongoing_session: AsyncSession,
        fields_values_filter: dict = None,
        order_by_fields: Optional[Union[str, Tuple[str, ...],
        UnaryExpression, Tuple[UnaryExpression, ...], None]] = (
                "some_model_field", "some_model_obj.field",),
        return_scalars: bool = True
) -> Sequence[Row[tuple[Any, ...]]] | Sequence[Row | RowMapping]:
    """return_scalars: bool: - if True returns scalar values,
    that can be used outside async connection context manager
    - if False returns sql alchemy rows, that disappear outside async
    connection context manager or may work not correctly. Use only inside
    async connection context manager with return_scalars = False"""
    try:
        orm_query = select(orm_model_class)

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
        if return_scalars:
            orm_model_rows = result.scalars().all()
        else:
            orm_model_rows = result.all()
        return orm_model_rows
    except Exception as error:
        log_text = (f"Getting orm model rows with flex query [ERROR]: \n"
                    f"error: {error} \n"
                    f"orm_model_class: {orm_model_class} \n"
                    f"fields_values_filter: {fields_values_filter} \n"
                    f"order_by_fields: {order_by_fields} \n")
        print(log_text)
        raise
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail=log_text)
