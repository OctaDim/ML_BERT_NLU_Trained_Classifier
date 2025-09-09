from typing import Dict

from sqlalchemy.orm import DeclarativeBase


def update_model_obj_no_commit(orm_model_object: DeclarativeBase,
                               new_update_data: Dict[str, any]):
    invalid_attributes = []
    model_class_name = orm_model_object.__class__.__name__

    for attr_name in new_update_data.keys():
        if not hasattr(orm_model_object, attr_name):
            invalid_attributes.append(attr_name)
    if invalid_attributes:
        log_error = (f"DB Not existing model object attribute name(s) [ERROR]:\n"
                     f"invalid_attributes: {invalid_attributes}\n"
                     f"model_class_name: {model_class_name}\n"
                     f"model_object: {orm_model_object}\n")
        print(log_error)
        raise AttributeError(log_error)

    for attr_name, attr_value in new_update_data.items():
        try:
            setattr(orm_model_object, attr_name, attr_value)
        except Exception as error:
            log_error = (f"DB Failed to set model object attribute [ERROR]: "
                         f"error: {error}\n"
                         f"attr_name: {attr_name}\n"
                         f"attr_value: {attr_value}\n"
                         f"model_class_name: {model_class_name}\n"
                         f"model_object: {orm_model_object}\n")
            print(log_error)
            raise type(error)(log_error) from error
    return orm_model_object
