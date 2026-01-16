from pydantic import BaseModel


class SaveRenamedClassInData(BaseModel):
    label_category_id: int
    model_class_name: str
    renamed_class_name: str
