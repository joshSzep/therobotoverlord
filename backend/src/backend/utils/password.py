import re


def validate_password(password: str) -> tuple[bool, str | None]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # Check for at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    # Check for at least one lowercase letter
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    # Check for at least one digit
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."

    # Check for at least one special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."

    return True, None


def is_common_password(password: str) -> bool:
    common_passwords = [
        "password",
        "123456",
        "qwerty",
        "admin",
        "welcome",
        "password123",
    ]
    return password.lower() in common_passwords
