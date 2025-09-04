def update_model_obj_no_commit(model_object, new_update_data: dict):
    invalid_attributes = []
    for attr_name in new_update_data.keys():
        if not hasattr(model_object, attr_name):
            invalid_attributes.append(attr_name)

    model_class = model_object.__class__.__name__

    if invalid_attributes:
        log_error = (f"DB Model object attribute name not exists [ERROR]:\n"
                     f"invalid_attributes: {invalid_attributes}\n"
                     f"model_class: {model_class}\n"
                     f"model_object: {model_object}\n")
        print(log_error)
        raise AttributeError(log_error)

    for attr_name, attr_value in new_update_data.items():
        try:
            setattr(model_object, attr_name, attr_value)
        except Exception as error:
            log_error = (f"DB Failed to set model object attribute [ERROR]: "
                         f"error: {error}\n"
                         f"attr_name: {attr_name}\n"
                         f"attr_value: {attr_value}\n"
                         f"model_class: {model_class}\n"
                         f"model_object: {model_object}\n")
            print(log_error)
            raise type(error)(log_error) from error
    return model_object
