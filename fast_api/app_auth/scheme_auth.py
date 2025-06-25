from pydantic import BaseModel


class AuthDataTest(BaseModel):
    username: str = "temp_username"
    password: str = "temp_password"
