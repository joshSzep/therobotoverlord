from unittest import mock
import uuid

from fastapi import Request
from fastapi.responses import HTMLResponse
import pytest

from backend.routes.html.home.index import home
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.post import PostList
from backend.schemas.post import PostResponse
from backend.schemas.topic import TopicList
from backend.schemas.topic import TopicResponse
from backend.schemas.user import UserSchema
from backend.utils.datetime import now_utc


@pytest.fixture
def mock_request() -> mock.MagicMock:
    """Returns a mock Request object."""
    return mock.MagicMock(spec=Request)


@pytest.fixture
def mock_user() -> UserResponse:
    """Returns a mock UserResponse object."""
    return UserResponse(
        id=uuid.uuid4(),
        email="test@example.com",
        display_name="Test User",
        is_verified=True,
        role="user",
        created_at=now_utc(),
        updated_at=now_utc(),
    )


@pytest.fixture
def mock_topics(mock_user: UserResponse) -> TopicList:
    """Returns a mock TopicList object."""
    author_schema = UserSchema.model_validate(mock_user.model_dump())
    topics = [
        TopicResponse(
            id=uuid.uuid4(),
            title="First Topic",
            description="Description for first topic",
            author=author_schema,
            created_at=now_utc(),
            updated_at=now_utc(),
            post_count=5,
            tags=[],
        ),
        TopicResponse(
            id=uuid.uuid4(),
            title="Second Topic",
            description="Description for second topic",
            author=author_schema,
            created_at=now_utc(),
            updated_at=now_utc(),
            post_count=3,
            tags=[],
        ),
    ]
    return TopicList(topics=topics, count=2)


@pytest.fixture
def mock_posts(mock_user: UserResponse) -> PostList:
    """Returns a mock PostList object."""
    author_schema = UserSchema.model_validate(mock_user.model_dump())
    posts = [
        PostResponse(
            id=uuid.uuid4(),
            content="First post content",
            author=author_schema,
            topic_id=uuid.uuid4(),
            parent_post_id=None,
            created_at=now_utc(),
            updated_at=now_utc(),
            reply_count=0,
        ),
        PostResponse(
            id=uuid.uuid4(),
            content="Second post content",
            author=author_schema,
            topic_id=uuid.uuid4(),
            parent_post_id=None,
            created_at=now_utc(),
            updated_at=now_utc(),
            reply_count=2,
        ),
    ]
    return PostList(posts=posts, count=2)


@pytest.mark.asyncio
async def test_home_authenticated_user(
    mock_request, mock_user, mock_topics, mock_posts
):
    """Test home page rendering with authenticated user."""
    # Arrange
    mock_html_content = "<html>Mock Home Page</html>"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.html.home.index.list_topics",
            new=mock.AsyncMock(return_value=mock_topics),
        ) as mock_list_topics,
        mock.patch(
            "backend.routes.html.home.index.list_posts",
            new=mock.AsyncMock(return_value=mock_posts),
        ) as mock_list_posts,
        mock.patch(
            "backend.routes.html.home.index.create_home_page",
            return_value=mock.MagicMock(__str__=lambda self: mock_html_content),
        ) as mock_create_page,
    ):
        # Act
        response = await home(request=mock_request, current_user=mock_user)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.body.decode() == mock_html_content  # type: ignore
        mock_list_topics.assert_called_once_with(skip=0, limit=5)
        mock_list_posts.assert_called_once_with(skip=0, limit=10)
        mock_create_page.assert_called_once_with(
            topics=mock_topics.topics,
            posts=mock_posts.posts,
            user=mock_user,
        )


@pytest.mark.asyncio
async def test_home_unauthenticated_user(mock_request, mock_topics, mock_posts):
    """Test home page rendering with unauthenticated user."""
    # Arrange
    mock_html_content = "<html>Mock Home Page</html>"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.html.home.index.list_topics",
            new=mock.AsyncMock(return_value=mock_topics),
        ) as mock_list_topics,
        mock.patch(
            "backend.routes.html.home.index.list_posts",
            new=mock.AsyncMock(return_value=mock_posts),
        ) as mock_list_posts,
        mock.patch(
            "backend.routes.html.home.index.create_home_page",
            return_value=mock.MagicMock(__str__=lambda self: mock_html_content),
        ) as mock_create_page,
    ):
        # Act
        response = await home(request=mock_request, current_user=None)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.body.decode() == mock_html_content  # type: ignore
        mock_list_topics.assert_called_once_with(skip=0, limit=5)
        mock_list_posts.assert_called_once_with(skip=0, limit=10)
        mock_create_page.assert_called_once_with(
            topics=mock_topics.topics,
            posts=mock_posts.posts,
            user=None,
        )


@pytest.mark.asyncio
async def test_home_empty_topics_and_posts(mock_request, mock_user):
    """Test home page rendering with empty topics and posts."""
    # Arrange
    empty_topics = TopicList(topics=[], count=0)
    empty_posts = PostList(posts=[], count=0)
    mock_html_content = "<html>Empty Home Page</html>"

    # Mock dependencies
    with (
        mock.patch(
            "backend.routes.html.home.index.list_topics",
            new=mock.AsyncMock(return_value=empty_topics),
        ) as mock_list_topics,
        mock.patch(
            "backend.routes.html.home.index.list_posts",
            new=mock.AsyncMock(return_value=empty_posts),
        ) as mock_list_posts,
        mock.patch(
            "backend.routes.html.home.index.create_home_page",
            return_value=mock.MagicMock(__str__=lambda self: mock_html_content),
        ) as mock_create_page,
    ):
        # Act
        response = await home(request=mock_request, current_user=mock_user)

        # Assert
        assert isinstance(response, HTMLResponse)
        assert response.body.decode() == mock_html_content  # type: ignore
        mock_list_topics.assert_called_once_with(skip=0, limit=5)
        mock_list_posts.assert_called_once_with(skip=0, limit=10)
        mock_create_page.assert_called_once_with(
            topics=[],
            posts=[],
            user=mock_user,
        )
