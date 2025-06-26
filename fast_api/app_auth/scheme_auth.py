from pydantic import BaseModel


class AuthDataBert(BaseModel):
    username: str = "temp_zxc"
    password: str = "temp_123"
