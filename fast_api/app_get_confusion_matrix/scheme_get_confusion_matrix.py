from pydantic import BaseModel


class ConfusionMatrixData(BaseModel):
    conf_mtrx_filename: str = ""
