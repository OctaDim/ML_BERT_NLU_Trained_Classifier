from typing import Type, Dict, List, Tuple

from fastapi import Query
from sqlalchemy import Select

from db_postgres.postgres_init.declarative_base_model import Base


def create_where_for_partial_query(
        orm_model_class: Type[Base],
        prior_orm_query: Select,
        fields_values_filter: Dict[str, any | List[any] | Tuple[any]]
) -> Query:
    if prior_orm_query is None:
        log_error = (f"DB creating WHERE for partition query [ERROR]:\n"
                     f"orm_query: {prior_orm_query}\n"
                     f"fields_values_filter: {fields_values_filter}\n")
        print(log_error)
        raise ValueError(log_error)

    invalid_attributes = []
    for field_name in fields_values_filter.keys():
        if not hasattr(orm_model_class, field_name):
            invalid_attributes.append(field_name)
    if invalid_attributes:
        log_error = (f"DB Filter by field(s) [ERROR]: "
                     f"Attribute(s) string name not found in model class\n"
                     f"orm_model_class: {orm_model_class}\n"
                     f"invalid_attributes: {invalid_attributes}\n"
                     f"fields_values_filter: {fields_values_filter}\n")
        print(log_error)
        raise AttributeError(log_error)

    try:
        for field_name, field_value in fields_values_filter.items():
            column = getattr(orm_model_class, field_name)
            if isinstance(field_value, bool):
                prior_orm_query = prior_orm_query.where(column.is_(field_value))
            else:
                if isinstance(field_value, (list, tuple)):
                    if None in field_value:
                        non_none_values = [v for v in field_value if v is not None]
                        prior_orm_query = prior_orm_query.where(
                            column.is_(None) | column.in_(non_none_values))
                    else:
                        prior_orm_query = prior_orm_query.where(column.in_(field_value))
                else:
                    prior_orm_query = prior_orm_query.where(column == field_value)
    except Exception as error:
        log_error = (f"Creating WHERE query by adding WHERE part [ERROR]: \n"
                     f"error: {error} \n"
                     f"orm_model_class: {orm_model_class} \n"
                     f"prior_orm_query: {prior_orm_query} \n"
                     f"invalid_attributes: {invalid_attributes} \n"
                     f"fields_values_filter: {fields_values_filter} \n")
        print(log_error)
        raise
    return prior_orm_query
