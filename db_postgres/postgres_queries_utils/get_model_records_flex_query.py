from typing import Union, Optional, Tuple, Type, Any, Sequence, List

from sqlalchemy import select, UnaryExpression, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from configs.settings import ALCHEMY_OPTIONS
from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_queries_utils.create_order_by_partial_query import (
    create_order_for_partial_query)
from db_postgres.postgres_queries_utils.create_where_partial_query import (
    create_where_for_partial_query)
from utils_common.exec_time_decorator import execution_time_decorator


@execution_time_decorator(in_seconds=True,
                          note="Get_model_recs_flex_query",
                          exec_time_logging=ALCHEMY_OPTIONS.ALCHEMY_QUERY_EXEC_TIME_LOGS)
async def get_model_rows_flex_query(
        orm_model_class: Type[Base],
        ongoing_session: AsyncSession,
        selected_fields: Optional[Union[List[str], Tuple[str, ...], str, None]] = None,
        fields_values_filter: dict = None,
        order_by_fields: Optional[Union[str, Tuple[str, ...],
        UnaryExpression, Tuple[UnaryExpression, ...],
        InstrumentedAttribute, None]] = (
                "field_name", "ModelClass.field_obj", "ModelClass.field_obj.desc()"),
        return_scalars: bool = True
) -> Sequence[Row[tuple[Any, ...]]] | Sequence[Row | RowMapping]:
    """return_scalars: bool: - if True returns scalar values,
    that can be used outside async connection context manager
    - if False returns sql alchemy rows, that disappear outside async
    connection context manager or may work not correctly. Use only inside
    async connection context manager with return_scalars = False"""
    try:
        # Selecting model columns by name
        if not selected_fields:
            orm_query = select(orm_model_class)  # All records
        else:
            if isinstance(selected_fields, str):
                fields_list = [selected_fields]
            elif isinstance(selected_fields, (tuple, list)):
                fields_list = selected_fields
            else:
                error_log = (f"DB Selecting model columns by field(s) [ERROR]:\n"
                             f"orm_model_class: {orm_model_class}\n"
                             f"selected_fields: {selected_fields}\n")
                print(error_log)
                raise ValueError(error_log)

            columns_to_select = []
            for select_field in fields_list:
                if hasattr(orm_model_class, select_field):
                    column_obj = getattr(orm_model_class, select_field)
                    if isinstance(column_obj, InstrumentedAttribute):
                        columns_to_select.append(column_obj)
                else:
                    error_log = (f"DB Select by field '{select_field}' skipped [ERROR]: "
                                 f"Attribute string name not found in model class\n"
                                 f"orm_model_class: {orm_model_class}\n"
                                 f"select_field: {select_field}\n"
                                 f"selected_fields: {selected_fields}\n")
                    print(error_log)
                    raise AttributeError(error_log)

            if columns_to_select:
                orm_query = select(*columns_to_select)
            else:
                orm_query = select(orm_model_class)  # All records

        # Creating filter flex query part
        if fields_values_filter:
            orm_query = create_where_for_partial_query(
                orm_model_class=orm_model_class,
                prior_orm_query=orm_query,
                fields_values_filter=fields_values_filter)

        # Creating order flex query part
        if order_by_fields is not None:  # ORM model field has no boolean property
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
