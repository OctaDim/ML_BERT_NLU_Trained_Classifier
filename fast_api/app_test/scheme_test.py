from pydantic import BaseModel


class IncomeDataTest(BaseModel):
    text_phrase: str
