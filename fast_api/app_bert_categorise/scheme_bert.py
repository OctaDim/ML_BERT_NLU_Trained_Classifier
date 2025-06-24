from pydantic import BaseModel


class IncomeDataBert(BaseModel):
    text_phrase: str
