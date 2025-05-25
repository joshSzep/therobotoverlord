"""Password validation and security utilities."""

import re


def validate_password(password: str) -> tuple[bool, str | None]:
    """Validate password strength.

    Args:
        password: The password to validate.

    Returns:
        A tuple containing:
        - bool: True if the password is valid, False otherwise.
        - Optional[str]: Error message if the password is invalid, None otherwise.
    """
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
    """Check if the password is a common password.

    This is a simplified implementation. In a production environment,
    you would want to check against a comprehensive list of common passwords.

    Args:
        password: The password to check.

    Returns:
        True if the password is common, False otherwise.
    """
    common_passwords = [
        "password",
        "123456",
        "qwerty",
        "admin",
        "welcome",
        "password123",
    ]
    return password.lower() in common_passwords
