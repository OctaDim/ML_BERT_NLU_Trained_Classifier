from typing import Tuple, Type, Union, Any

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import Query

from db_postgres.postgres_async_conn.pgs_async_connection import Base


def create_order_by_partial_query(
        model_class: Union[Type[Base], Type[Any]],
        prior_filter_query: Query,
        order_by_fields: Union[
            str, Tuple[str, ...], UnaryExpression, Tuple[UnaryExpression, ...],
            None] = ("id",)):
    """
    Create partial ordering query expression for ordering sql alchemy models.
    :param model_class: Model class object <Model>
    :param prior_filter_query: sql alchemy query expression before ordering query,
    e.g. prior_filter_query = session.query(<Model>).filter(<Model.id> == model_id)
    :param order_by_fields: Tuple: Fields string name(s) or model column(s),
    e.g.("field1_str_name", ) or (<Model>.<field1>, <Model>.<field2>.desc())
    (for model columns additional methods can be used, e.g. <Model>.<field>.desc())
    :return: sql alchemy partial ordering query expression or previous query expression,
     if order_by_fields was defined wrong and model has no such attributes
    """
    if order_by_fields is None:
        return prior_filter_query

    order_query = prior_filter_query

    if isinstance(order_by_fields, tuple):
        order_by_fields_validated = order_by_fields
    else:
        order_by_fields_validated = (order_by_fields,)

    if order_by_fields_validated:
        for order_field in order_by_fields_validated:
            if isinstance(order_field, str):
                if hasattr(model_class, order_field):
                    order_query = order_query.order_by(order_field)
                else:
                    print(f"\tOrder by field '{order_field}' skipped [ERROR: "
                          f"Attribute string name not found in model class: "
                          f"'{model_class}'\n")
            else:
                order_query = order_query.order_by(order_field)
    return order_query
