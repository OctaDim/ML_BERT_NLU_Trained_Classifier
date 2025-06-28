from pydantic import BaseModel


class TextCategoryDataBert(BaseModel):
    update_text: str = "test new text"
    update_category: str = "test new category"
