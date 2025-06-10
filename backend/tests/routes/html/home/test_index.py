from unittest import mock

from fastapi import Request
from fastapi.responses import HTMLResponse
import pytest

from backend.routes.html.home.index import home


@pytest.fixture
def mock_request():
    """Mock FastAPI request for testing."""
    request = mock.MagicMock(spec=Request)
    request.url = mock.MagicMock()
    request.headers = {}
    request.cookies = {}
    return request


@pytest.fixture
def mock_user():
    """Mock authenticated user for testing."""
    user = mock.MagicMock()
    user.id = "test-user-id"
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.is_verified = True
    return user


@pytest.fixture
def mock_topics():
    """Mock topics for testing."""
    topics_data = mock.MagicMock()
    topics = []
    for i in range(5):
        topic = mock.MagicMock()
        topic.id = f"topic-{i}"
        topic.name = f"Topic {i}"
        topics.append(topic)
    topics_data.topics = topics
    return topics_data


@pytest.fixture
def mock_posts():
    """Mock posts for testing."""
    posts_data = mock.MagicMock()
    posts = []
    for i in range(5):
        post = mock.MagicMock()
        post.id = f"post-{i}"
        post.content = f"Post content {i}"
        post.author = mock.MagicMock()
        post.author.display_name = f"Author {i}"
        post.created_at = mock.MagicMock()
        posts.append(post)
    posts_data.posts = posts
    return posts_data


@pytest.mark.asyncio
async def test_home_authenticated_user(
    mock_request, mock_user, mock_topics, mock_posts
):
    """Test home page rendering for authenticated user."""
    # Arrange
    with (
        mock.patch("backend.routes.html.home.index.list_topics") as mock_list_topics,
        mock.patch("backend.routes.html.home.index.list_posts") as mock_list_posts,
        mock.patch(
            "backend.routes.html.home.index.create_home_page"
        ) as mock_create_home_page,
    ):
        mock_list_topics.return_value = mock_topics
        mock_list_posts.return_value = mock_posts
        mock_create_home_page.return_value = "<html>Home Page</html>"

        # Act
        result = await home(request=mock_request, current_user=mock_user)

        # Assert
        assert isinstance(result, HTMLResponse)
        mock_list_topics.assert_called_once_with(skip=0, limit=5)
        mock_list_posts.assert_called_once_with(skip=0, limit=10)
        mock_create_home_page.assert_called_once_with(
            topics=mock_topics.topics, posts=mock_posts.posts, user=mock_user
        )


@pytest.mark.asyncio
async def test_home_unauthenticated_user(mock_request, mock_topics, mock_posts):
    """Test home page rendering for unauthenticated user."""
    # Arrange
    with (
        mock.patch("backend.routes.html.home.index.list_topics") as mock_list_topics,
        mock.patch("backend.routes.html.home.index.list_posts") as mock_list_posts,
        mock.patch(
            "backend.routes.html.home.index.create_home_page"
        ) as mock_create_home_page,
    ):
        mock_list_topics.return_value = mock_topics
        mock_list_posts.return_value = mock_posts
        mock_create_home_page.return_value = "<html>Home Page</html>"

        # Act
        result = await home(request=mock_request, current_user=None)

        # Assert
        assert isinstance(result, HTMLResponse)
        mock_list_topics.assert_called_once_with(skip=0, limit=5)
        mock_list_posts.assert_called_once_with(skip=0, limit=10)
        mock_create_home_page.assert_called_once_with(
            topics=mock_topics.topics, posts=mock_posts.posts, user=None
        )


@pytest.mark.asyncio
async def test_home_no_data(mock_request, mock_user):
    """Test home page rendering when no topics or posts exist."""
    # Arrange
    empty_topics = mock.MagicMock()
    empty_topics.topics = []
    empty_posts = mock.MagicMock()
    empty_posts.posts = []

    with (
        mock.patch("backend.routes.html.home.index.list_topics") as mock_list_topics,
        mock.patch("backend.routes.html.home.index.list_posts") as mock_list_posts,
        mock.patch(
            "backend.routes.html.home.index.create_home_page"
        ) as mock_create_home_page,
    ):
        mock_list_topics.return_value = empty_topics
        mock_list_posts.return_value = empty_posts
        mock_create_home_page.return_value = "<html>Home Page - No Data</html>"

        # Act
        result = await home(request=mock_request, current_user=mock_user)

        # Assert
        assert isinstance(result, HTMLResponse)
        mock_create_home_page.assert_called_once_with(
            topics=[], posts=[], user=mock_user
        )


@pytest.mark.asyncio
async def test_home_database_error(mock_request, mock_user):
    """Test home page handling of database errors."""
    # Arrange
    db_error = Exception("Database connection error")

    with mock.patch("backend.routes.html.home.index.list_topics", side_effect=db_error):
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await home(request=mock_request, current_user=mock_user)

        assert exc_info.value == db_error
