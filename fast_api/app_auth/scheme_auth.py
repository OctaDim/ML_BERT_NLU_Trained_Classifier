from pydantic import BaseModel


class AuthDataBert(BaseModel):
    username: str
    password: str
    # username: str = "temp_zxc"
    # password: str = "temp_123"
