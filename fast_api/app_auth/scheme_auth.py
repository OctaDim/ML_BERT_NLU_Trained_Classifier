from pydantic import BaseModel


class AuthDataBert(BaseModel):
    # username: str
    # password: str
    username: str = "temp_zxc"  # DEBUG ONLY
    password: str = "temp_123"  # DEBUG ONLY
