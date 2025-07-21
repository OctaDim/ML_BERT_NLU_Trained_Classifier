from pydantic import BaseModel


class SingleCategoryDataBert(BaseModel):
    update_category: str = "test new single category"
