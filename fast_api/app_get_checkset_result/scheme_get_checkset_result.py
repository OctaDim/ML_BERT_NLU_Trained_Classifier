from pydantic import BaseModel


class CheckSetData(BaseModel):
    checkset_filename: str = ""
