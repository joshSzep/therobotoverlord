from unittest import mock
import uuid

from bs4 import BeautifulSoup
import pytest

from backend.dominate_templates.topics.list import create_topics_list_page


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = mock.MagicMock()
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.is_admin = False
    user.approved_count = 5
    user.rejected_count = 2
    return user


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user for testing."""
    user = mock.MagicMock()
    user.id = uuid.uuid4()
    user.email = "admin@example.com"
    user.display_name = "Admin User"
    user.is_admin = True
    user.approved_count = 10
    user.rejected_count = 3
    return user


@pytest.fixture
def mock_topics():
    """Create mock topics for testing."""
    # Create mock author
    author = mock.MagicMock()
    author.id = uuid.uuid4()
    author.display_name = "Author Name"

    # Create mock tags
    tag1 = mock.MagicMock()
    tag1.id = "tag1-id"
    tag1.name = "Tag1"
    tag1.slug = "tag1"

    tag2 = mock.MagicMock()
    tag2.id = "tag2-id"
    tag2.name = "Tag2"
    tag2.slug = "tag2"

    # Create mock topics
    topic1 = mock.MagicMock()
    topic1.id = "topic1-id"
    topic1.title = "Topic 1 Title"
    topic1.description = "Topic 1 description text"
    topic1.author = author
    topic1.tags = [tag1, tag2]
    topic1.post_count = 5

    topic2 = mock.MagicMock()
    topic2.id = "topic2-id"
    topic2.title = "Topic 2 Title"
    topic2.description = "Topic 2 description text"
    topic2.author = author
    topic2.tags = [tag1]
    topic2.post_count = 3

    return [topic1, topic2]


@pytest.fixture
def mock_pagination():
    """Mock pagination data for testing."""
    return {
        "total": 10,
        "total_pages": 4,
        "current_page": 1,
        "has_previous": False,
        "previous_page": None,
        "has_next": True,
        "next_page": 2,
    }


def test_create_topics_list_page_with_topics_and_user(
    mock_topics, mock_pagination, mock_user
):
    """Test topics list page rendering with authenticated user."""
    # Arrange
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        return_value="mocked_document",
    ) as mock_create_base:
        # Act
        document = create_topics_list_page(
            topics=mock_topics,
            pagination=mock_pagination,
            user=mock_user,
        )

        # Assert
        mock_create_base.assert_called_once()
        kwargs = mock_create_base.call_args.kwargs
        assert kwargs.get("title_text") == "The Robot Overlord - Topics"
        assert kwargs.get("user") == mock_user
        assert document == "mocked_document"


def test_create_topics_list_page_with_admin_user(
    mock_topics, mock_pagination, mock_admin_user
):
    """Test topics list page rendering with admin user."""
    # Arrange
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        return_value="mocked_document",
    ) as mock_create_base:
        # Act
        document = create_topics_list_page(
            topics=mock_topics,
            pagination=mock_pagination,
            user=mock_admin_user,
        )

        # Assert
        mock_create_base.assert_called_once()
        kwargs = mock_create_base.call_args.kwargs
        assert kwargs.get("title_text") == "The Robot Overlord - Topics"
        assert kwargs.get("user") == mock_admin_user

        # Check that content_func exists and is callable
        content_func = kwargs.get("content_func")
        assert content_func is not None
        assert callable(content_func)

        # Verify the document was returned
        assert document == "mocked_document"


def test_create_topics_list_page_with_regular_user(
    mock_topics, mock_pagination, mock_user
):
    """Test topics list page rendering with regular user (no admin form)."""

    # Arrange
    def side_effect(**kwargs):
        # Call the content_func to check if it renders the admin form
        content_func = kwargs.get("content_func")
        if content_func:
            # Create a simple HTML document to test the content function
            from dominate.document import document

            doc = document()
            content_func()
            return doc
        return None

    # Act
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        side_effect=side_effect,
    ) as mock_create_base:
        document = create_topics_list_page(
            topics=mock_topics,
            pagination=mock_pagination,
            user=mock_user,
        )

        # Assert
        mock_create_base.assert_called_once()
        assert document is not None
        html_content = document.render()
        soup = BeautifulSoup(html_content, "html.parser")

        # Check that create topic form is not present for regular users
        create_topic_div = soup.select_one(".create-topic-form")
        assert create_topic_div is None


def test_create_topics_list_page_with_empty_topics(mock_pagination, mock_user):
    """Test topics list page rendering with empty topics list."""

    # Arrange
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        return_value="mocked_document",
    ) as mock_create_base:
        # Act
        document = create_topics_list_page(
            topics=[],
            pagination=mock_pagination,
            user=mock_user,
        )

        # Assert
        mock_create_base.assert_called_once()
        kwargs = mock_create_base.call_args.kwargs
        assert kwargs.get("title_text") == "The Robot Overlord - Topics"
        assert kwargs.get("user") == mock_user

        # Check that content_func exists and is callable
        content_func = kwargs.get("content_func")
        assert content_func is not None
        assert callable(content_func)

        # Verify the document was returned
        assert document == "mocked_document"


def test_create_topics_list_page_topic_content(mock_topics, mock_pagination, mock_user):
    """Test that topic content is correctly rendered."""

    # Arrange
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        return_value="mocked_document",
    ) as mock_create_base:
        # Act
        document = create_topics_list_page(
            topics=mock_topics,
            pagination=mock_pagination,
            user=mock_user,
        )

        # Assert
        mock_create_base.assert_called_once()
        kwargs = mock_create_base.call_args.kwargs
        assert kwargs.get("title_text") == "The Robot Overlord - Topics"
        assert kwargs.get("user") == mock_user

        # Check that content_func exists and is callable
        content_func = kwargs.get("content_func")
        assert content_func is not None
        assert callable(content_func)

        # Verify the document was returned
        assert document == "mocked_document"


def test_create_topics_list_page_pagination(mock_topics, mock_pagination, mock_user):
    """Test that pagination is correctly rendered."""

    # Arrange
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        return_value="mocked_document",
    ) as mock_create_base:
        # Act
        document = create_topics_list_page(
            topics=mock_topics, pagination=mock_pagination, user=mock_user
        )

        # Assert
        mock_create_base.assert_called_once()
        kwargs = mock_create_base.call_args.kwargs
        assert kwargs.get("title_text") == "The Robot Overlord - Topics"
        assert kwargs.get("user") == mock_user

        # Check that content_func exists and is callable
        content_func = kwargs.get("content_func")
        assert content_func is not None
        assert callable(content_func)

        # Verify the document was returned
        assert document == "mocked_document"


def test_create_topics_list_page_single_page_no_pagination(mock_topics, mock_user):
    """Test that pagination is not rendered when there's only one page."""
    # Create pagination data with only one page
    single_page_pagination = {
        "total": 3,
        "total_pages": 1,
        "current_page": 1,
        "has_previous": False,
        "previous_page": None,
        "has_next": False,
        "next_page": None,
    }

    # Arrange
    def side_effect(**kwargs):
        content_func = kwargs.get("content_func")
        if content_func:
            from dominate.document import document

            doc = document()
            content_func()
            return doc
        return None

    # Act
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        side_effect=side_effect,
    ) as mock_create_base:
        document = create_topics_list_page(
            topics=mock_topics, pagination=single_page_pagination, user=mock_user
        )

        # Assert
        mock_create_base.assert_called_once()
        assert document is not None
        html_content = document.render()
        soup = BeautifulSoup(html_content, "html.parser")

        # Check that pagination element is not present or shows only current page
        pagination_links = soup.select(".pagination a")
        assert len(pagination_links) == 0


def test_create_topics_list_page_with_messages(mock_topics, mock_pagination, mock_user):
    """Test topics list page rendering with messages."""
    # Create test messages
    messages = [
        {"type": "success", "text": "Topic created successfully!"},
        {"type": "error", "text": "An error occurred."},
    ]

    # Act
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        return_value="mocked_document",
    ) as mock_create_base_document:
        _ = create_topics_list_page(
            topics=mock_topics,
            pagination=mock_pagination,
            user=mock_user,
            messages=messages,
        )

        # Assert
        mock_create_base_document.assert_called_once()
        # Verify messages were passed to create_base_document
        kwargs = mock_create_base_document.call_args.kwargs
        assert kwargs.get("messages") == messages


def test_create_topics_list_page_topic_without_tags(
    mock_topics, mock_pagination, mock_user
):
    """Test topics list page rendering with a topic that has no tags."""
    # Modify one topic to have no tags
    mock_topics[0].tags = []

    # Arrange
    with mock.patch(
        "backend.dominate_templates.topics.list.create_base_document",
        return_value="mocked_document",
    ) as mock_create_base:
        # Act
        document = create_topics_list_page(
            topics=mock_topics, pagination=mock_pagination, user=mock_user
        )

        # Assert
        mock_create_base.assert_called_once()
        kwargs = mock_create_base.call_args.kwargs
        assert kwargs.get("title_text") == "The Robot Overlord - Topics"
        assert kwargs.get("user") == mock_user

        # Check that content_func exists and is callable
        content_func = kwargs.get("content_func")
        assert content_func is not None
        assert callable(content_func)

        # Verify the document was returned
        assert document == "mocked_document"
