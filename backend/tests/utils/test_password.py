import pytest

from backend.utils.password import is_common_password
from backend.utils.password import validate_password


@pytest.mark.parametrize(
    "password,expected_valid,expected_error",
    [
        # Valid passwords
        ("StrongP@ss123", True, None),
        ("C0mpl3x!P@ssw0rd", True, None),
        ("Abcd1234!", True, None),
        # Too short
        ("Abc1!", False, "Password must be at least 8 characters long."),
        # No uppercase
        ("password123!", False, "Password must contain at least one uppercase letter."),
        # No lowercase
        ("PASSWORD123!", False, "Password must contain at least one lowercase letter."),
        # No digit
        ("PasswordNoDigit!", False, "Password must contain at least one digit."),
        # No special char
        ("Password123", False, "Password must contain at least one special character."),
    ],
)
def test_validate_password(
    password: str, expected_valid: bool, expected_error: str | None
) -> None:
    """Test password validation with various inputs."""
    # Act
    valid, error = validate_password(password)

    # Assert
    assert valid == expected_valid
    assert error == expected_error


@pytest.mark.parametrize(
    "password,expected_result",
    [
        # Common passwords
        ("password", True),
        ("123456", True),
        ("qwerty", True),
        ("admin", True),
        ("welcome", True),
        ("password123", True),
        # Variations of common passwords (should still match because of .lower())
        ("PASSWORD", True),
        ("Password", True),
        ("ADMIN", True),
        # Non-common passwords
        ("StrongP@ss123", False),
        ("C0mpl3x!P@ssw0rd", False),
        ("ThisIsNotCommon123!", False),
    ],
)
def test_is_common_password(password: str, expected_result: bool) -> None:
    """Test checking if a password is common."""
    # Act
    result = is_common_password(password)

    # Assert
    assert result == expected_result


def test_is_common_password_edge_cases() -> None:
    """Test edge cases for common password check."""
    # Empty string
    assert not is_common_password("")

    # Very long password
    long_password = "a" * 100
    assert not is_common_password(long_password)

    # Password with special characters
    assert not is_common_password("P@$$w0rd!")

    # Unicode characters
    assert not is_common_password("üñîçødé123")
