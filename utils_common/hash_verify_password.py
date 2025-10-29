import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(
        plain_password: str,
        hashed_password: str,
        compare_not_hashed: bool = False
) -> bool:
    if compare_not_hashed:
        is_password_valid = plain_password == hashed_password
    else:
        is_password_valid = bcrypt.checkpw(
            password=plain_password.encode(),
            hashed_password=hashed_password.encode())
    return is_password_valid
