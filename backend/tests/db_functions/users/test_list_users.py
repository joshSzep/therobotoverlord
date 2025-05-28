# Standard library imports
from unittest import mock
import uuid

# Third-party imports
import pytest
from tortoise.exceptions import OperationalError

# Project-specific imports
from backend.db.models.user import User
from backend.db_functions.users.list_users import list_users
from backend.schemas.user import UserSchema


@pytest.fixture
def mock_users() -> list[mock.MagicMock]:
    users = []
    for i in range(3):
        user = mock.MagicMock(spec=User)
        user.id = uuid.uuid4()
        user.email = f"test{i}@example.com"
        user.display_name = f"Test User {i}"
        user.is_verified = i % 2 == 0
        user.last_login = mock.MagicMock()
        user.failed_login_attempts = i
        user.is_locked = i == 2
        user.role = "user"
        user.created_at = mock.MagicMock()
        user.updated_at = mock.MagicMock()
        users.append(user)
    return users


@pytest.fixture
def mock_user_schemas(mock_users) -> list[UserSchema]:
    return [
        UserSchema(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            is_verified=user.is_verified,
            role=user.role,
            is_locked=user.is_locked,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
        )
        for user in mock_users
    ]


@pytest.mark.asyncio
async def test_list_users_success(mock_users, mock_user_schemas) -> None:
    # Arrange
    test_skip = 0
    test_limit = 20
    test_count = len(mock_users)

    # Mock the database query - RULE #10 compliance: only operates on User model
    with (
        mock.patch.object(User, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch(
            "backend.db_functions.users.list_users.user_to_schema",
            new=mock.AsyncMock(side_effect=mock_user_schemas),
        ) as mock_converter,
    ):
        # Mock the count and query methods
        mock_all.return_value.count = mock.AsyncMock(return_value=test_count)
        mock_all.return_value.offset = mock.MagicMock(
            return_value=mock_all.return_value
        )
        mock_all.return_value.limit = mock.AsyncMock(return_value=mock_users)

        # Act
        result, count = await list_users(skip=test_skip, limit=test_limit)

        # Assert
        assert result is not None
        assert len(result) == len(mock_users)
        assert count == test_count

        # Verify function calls
        mock_all.assert_called()
        mock_all.return_value.count.assert_called_once()
        mock_all.return_value.offset.assert_called_once_with(test_skip)
        mock_all.return_value.limit.assert_called_once_with(test_limit)

        # Verify converter was called for each user
        assert mock_converter.call_count == len(mock_users)
        for i, user in enumerate(mock_users):
            mock_converter.assert_any_call(user)

        # Verify schema objects are returned (RULE #5)
        for user_schema in result:
            assert isinstance(user_schema, UserSchema)


@pytest.mark.asyncio
async def test_list_users_empty() -> None:
    # Arrange
    test_skip = 0
    test_limit = 20
    test_count = 0

    # Mock the database query
    with (
        mock.patch.object(User, "all", return_value=mock.MagicMock()) as mock_all,
    ):
        # Mock the count and query methods
        mock_all.return_value.count = mock.AsyncMock(return_value=test_count)
        mock_all.return_value.offset = mock.MagicMock(
            return_value=mock_all.return_value
        )
        mock_all.return_value.limit = mock.AsyncMock(return_value=[])

        # Act
        result, count = await list_users(skip=test_skip, limit=test_limit)

        # Assert
        assert result is not None
        assert len(result) == 0
        assert count == 0

        # Verify function calls
        mock_all.assert_called()
        mock_all.return_value.count.assert_called_once()
        mock_all.return_value.offset.assert_called_once_with(test_skip)
        mock_all.return_value.limit.assert_called_once_with(test_limit)


@pytest.mark.asyncio
async def test_list_users_with_pagination() -> None:
    # Arrange
    test_skip = 5
    test_limit = 10
    test_count = 25
    mock_page_users = [mock.MagicMock(spec=User) for _ in range(10)]
    mock_schemas = [mock.MagicMock(spec=UserSchema) for _ in range(10)]

    # Mock the database query
    with (
        mock.patch.object(User, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch(
            "backend.db_functions.users.list_users.user_to_schema",
            new=mock.AsyncMock(side_effect=mock_schemas),
        ) as mock_converter,
    ):
        # Mock the count and query methods
        mock_all.return_value.count = mock.AsyncMock(return_value=test_count)
        mock_all.return_value.offset = mock.MagicMock(
            return_value=mock_all.return_value
        )
        mock_all.return_value.limit = mock.AsyncMock(return_value=mock_page_users)

        # Act
        result, count = await list_users(skip=test_skip, limit=test_limit)

        # Assert
        assert result is not None
        assert len(result) == len(mock_page_users)
        assert count == test_count

        # Verify function calls
        mock_all.assert_called()
        mock_all.return_value.count.assert_called_once()
        mock_all.return_value.offset.assert_called_once_with(test_skip)
        mock_all.return_value.limit.assert_called_once_with(test_limit)

        # Verify converter was called for each user
        assert mock_converter.call_count == len(mock_page_users)


@pytest.mark.asyncio
async def test_list_users_database_error() -> None:
    # Arrange
    test_skip = 0
    test_limit = 20
    db_error = OperationalError("Database error")

    # Mock the database query
    with mock.patch.object(User, "all", return_value=mock.MagicMock()) as mock_all:
        # Mock the count method to raise an error
        mock_all.return_value.count = mock.AsyncMock(side_effect=db_error)

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await list_users(skip=test_skip, limit=test_limit)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_all.assert_called()
        mock_all.return_value.count.assert_called_once()


@pytest.mark.asyncio
async def test_list_users_query_error() -> None:
    # Arrange
    test_skip = 0
    test_limit = 20
    test_count = 10
    db_error = OperationalError("Query error")

    # Mock the database query
    with mock.patch.object(User, "all", return_value=mock.MagicMock()) as mock_all:
        # Mock the count method to succeed but the query to fail
        mock_all.return_value.count = mock.AsyncMock(return_value=test_count)
        mock_all.return_value.offset = mock.MagicMock(
            return_value=mock_all.return_value
        )
        mock_all.return_value.limit = mock.AsyncMock(side_effect=db_error)

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            await list_users(skip=test_skip, limit=test_limit)

        # Verify the exception is propagated correctly
        assert exc_info.value == db_error
        mock_all.assert_called()
        mock_all.return_value.count.assert_called_once()
        mock_all.return_value.offset.assert_called_once_with(test_skip)
        mock_all.return_value.limit.assert_called_once_with(test_limit)


@pytest.mark.asyncio
async def test_list_users_converter_error() -> None:
    # Arrange
    test_skip = 0
    test_limit = 20
    test_count = 3
    mock_users = [mock.MagicMock(spec=User) for _ in range(3)]
    converter_error = ValueError("Converter error")

    # Mock the database query
    with (
        mock.patch.object(User, "all", return_value=mock.MagicMock()) as mock_all,
        mock.patch(
            "backend.db_functions.users.list_users.user_to_schema",
            new=mock.AsyncMock(side_effect=converter_error),
        ) as mock_converter,
    ):
        # Mock the count and query methods
        mock_all.return_value.count = mock.AsyncMock(return_value=test_count)
        mock_all.return_value.offset = mock.MagicMock(
            return_value=mock_all.return_value
        )
        mock_all.return_value.limit = mock.AsyncMock(return_value=mock_users)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await list_users(skip=test_skip, limit=test_limit)

        # Verify the exception is propagated correctly
        assert exc_info.value == converter_error
        mock_all.assert_called()
        mock_all.return_value.count.assert_called_once()
        mock_all.return_value.offset.assert_called_once_with(test_skip)
        mock_all.return_value.limit.assert_called_once_with(test_limit)
        mock_converter.assert_called_once_with(mock_users[0])
