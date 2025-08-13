from typing import Annotated

from fastapi import File, Form, UploadFile
from pydantic import BaseModel


class UniqueLearnFileData(BaseModel):
    pass
