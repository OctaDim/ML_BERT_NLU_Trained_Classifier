from typing import Union

from fastapi import HTTPException, status

from configs.settings import API_TEST_PASSWORD, API_TEST_USERNAME


def verify_username_password(username: str, password: str
                             ) -> Union[bool, HTTPException]:
    if username != API_TEST_USERNAME or password != API_TEST_PASSWORD:
        log_text = (f"Wrong username or password [ERROR]:"
                    f"username: {username}, password: *****")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=log_text)
    return True
