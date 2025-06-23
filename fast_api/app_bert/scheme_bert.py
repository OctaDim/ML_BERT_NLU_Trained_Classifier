from pydantic import BaseModel


class IncomeData(BaseModel):
    text_phrase: str
