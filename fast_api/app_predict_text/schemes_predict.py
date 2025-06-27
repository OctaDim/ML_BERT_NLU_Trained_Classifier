from pydantic import BaseModel


class PredictDataBert(BaseModel):
    text_phrase: str = "да, конечно приду"
