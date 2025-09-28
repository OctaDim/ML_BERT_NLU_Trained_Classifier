from typing import Tuple, Type, Union

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Query

from db_postgres.postgres_async_conn.pgs_async_connection import Base


def create_order_for_partial_query(
        orm_model_class: Type[Base],
        prior_orm_query: Query,
        order_by_fields: Union[
            str, Tuple[str, ...], UnaryExpression, Tuple[UnaryExpression, ...],
            None] = ("id",)):
    """
    Create partial ordering query expression for ordering sql alchemy models.
    :param orm_model_class: Model class object <Model>
    :param prior_orm_query: sql alchemy query expression before ordering query,
    e.g. prior_filter_query = session.query(<Model>).filter(<Model.id> == model_id)
    :param order_by_fields: Tuple: Fields string name(s) or model column(s),
    e.g.("field1_str_name", ) or (<Model>.<field1>, <Model>.<field2>.desc())
    (for model columns additional methods can be used, e.g. <Model>.<field>.desc())
    :return: sql alchemy partial ordering query expression or previous query expression,
     if order_by_fields was defined wrong and model has no such attributes
    """
    if prior_orm_query is None:
        log_error = (f"DB creating ORDER BY for partition query [ERROR]:\n"
                     f"orm_query: {prior_orm_query}\n"
                     f"order_by_fields: {order_by_fields}\n")
        print(log_error)
        raise ValueError(log_error)

    if order_by_fields is None:
        print(f"DB creating order for partition query skipped [ERROR]:\n"
              f"order_by_fields: {order_by_fields}\n")
        return prior_orm_query

    order_query = prior_orm_query

    if isinstance(order_by_fields, tuple):
        order_by_fields_validated = order_by_fields
    else:
        order_by_fields_validated = (order_by_fields,)

    try:
        if order_by_fields_validated:
            for order_field in order_by_fields_validated:
                if order_field in ["field_name", "ModelClass.field_obj",
                                   "ModelClass.field_obj.desc()"]:
                    continue
                if isinstance(order_field, str):
                    if hasattr(orm_model_class, order_field):
                        order_query = order_query.order_by(order_field)
                    else:
                        error_log = (
                            f"DB Order by field '{order_field}' [ERROR]: "
                            f"Attribute string name not found in model class\n"
                            f"orm_model_class: {orm_model_class}\n"
                            f"order_field: {order_field}\n"
                            f"order_by_fields: {order_by_fields}\n")
                        print(error_log)
                        raise AttributeError(error_log)
                else:
                    order_query = order_query.order_by(order_field)
    except Exception as error:
        log_error = (f"Creating ORDER BY query by adding ORDER BY part [ERROR]: \n"
                     f"error: {error} \n"
                     f"orm_model_class: {orm_model_class} \n"
                     f"order_by_fields: {order_by_fields} \n")
        print(log_error)
        raise
    return order_query
