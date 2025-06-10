from unittest import mock
import uuid

from bs4 import BeautifulSoup
import pytest

from backend.dominate_templates.base import create_base_document
from backend.dominate_templates.base import create_base_page


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


def test_create_base_document_basic():
    """Test basic base document creation without user or content."""
    # Arrange & Act
    document = create_base_document(title_text="Test Title")

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check title
    assert soup.title.text == "Test Title"

    # Check basic structure
    assert soup.head is not None
    assert soup.body is not None
    assert soup.select_one(".site-header") is not None
    assert soup.select_one(".content") is not None
    assert soup.select_one("footer") is not None

    # Check site title
    site_title = soup.select_one(".site-title")
    assert site_title is not None
    assert site_title.text == "THE ROBOT OVERLORD"
    assert site_title["href"] == "/html/topics/"


def test_create_base_document_with_user(mock_user):
    """Test base document creation with authenticated user."""
    # Arrange & Act
    document = create_base_document(title_text="Test Title", user=mock_user)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check user info section
    user_info = soup.select_one(".user-info")
    assert user_info is not None

    # Check user name link
    user_name_link = user_info.select_one(".user-name")
    assert user_name_link is not None
    assert user_name_link.text == "Test User"
    assert user_name_link["href"] == f"/html/profile/{mock_user.id}/"

    # Check approval/rejection counters
    approved_count = user_info.select_one(".approved-count")
    assert approved_count is not None
    assert "5" in approved_count.text

    rejected_count = user_info.select_one(".rejected-count")
    assert rejected_count is not None
    assert "2" in rejected_count.text


def test_create_base_document_without_user():
    """Test base document creation without user (anonymous)."""
    # Arrange & Act
    document = create_base_document(title_text="Test Title", user=None)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check user info section
    user_info = soup.select_one(".user-info")
    assert user_info is not None

    # Check login link
    login_link = user_info.select_one(".user-name")
    assert login_link is not None
    assert login_link.text == "CITIZEN"
    assert login_link["href"] == "/html/auth/login/"

    # Check calibration text
    assert "YOUR LOGIC REQUIRES CALIBRATION" in user_info.text


def test_create_base_document_with_content_func():
    """Test base document creation with content function."""

    # Arrange
    def content_function():
        from dominate.tags import div
        from dominate.tags import h2
        from dominate.tags import p

        with div(cls="test-content"):
            h2("Test Content Heading")
            p("This is test content.")

    # Act
    document = create_base_document(
        title_text="Test Title", content_func=content_function
    )

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check content
    content_div = soup.select_one(".test-content")
    assert content_div is not None
    assert content_div.select_one("h2").text == "Test Content Heading"
    assert content_div.select_one("p").text == "This is test content."


def test_create_base_document_with_head_content_func():
    """Test base document creation with head content function."""

    # Arrange
    def head_content_function():
        from dominate.tags import meta
        from dominate.tags import script

        meta(name="description", content="Test description")
        script(type="text/javascript", src="/static/js/test.js")

    # Act
    document = create_base_document(
        title_text="Test Title", head_content_func=head_content_function
    )

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check head content
    meta_tag = soup.select_one('meta[name="description"]')
    assert meta_tag is not None
    assert meta_tag["content"] == "Test description"

    script_tag = soup.select_one('script[src="/static/js/test.js"]')
    assert script_tag is not None
    assert script_tag["type"] == "text/javascript"


def test_create_base_document_with_messages():
    """Test base document creation with messages."""
    # Arrange
    messages = [
        {"type": "success", "text": "Operation successful!"},
        {"type": "error", "text": "An error occurred."},
    ]

    # Act
    document = create_base_document(title_text="Test Title", messages=messages)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check messages
    message_divs = soup.select(".message")
    assert len(message_divs) == 2

    success_message = soup.select_one(".message.success")
    assert success_message is not None
    assert success_message.text == "Operation successful!"

    error_message = soup.select_one(".message.error")
    assert error_message is not None
    assert error_message.text == "An error occurred."


def test_create_base_page(mock_user):
    """Test create_base_page function."""
    # Arrange & Act
    with mock.patch(
        "backend.dominate_templates.base.create_base_document",
        return_value="mocked_document",
    ) as mock_create_base_document:
        document = create_base_page(
            title="Test Page", current_user=mock_user, is_admin=True
        )

    # Assert
    mock_create_base_document.assert_called_once()
    kwargs = mock_create_base_document.call_args.kwargs
    assert kwargs.get("title_text") == "Test Page"
    assert kwargs.get("user") == mock_user
    assert document == "mocked_document"


def test_create_base_document_with_username_starting_with_at(mock_user):
    """Test base document creation with username starting with @ symbol."""
    # Arrange
    mock_user.display_name = "@TestUser"

    # Act
    document = create_base_document(title_text="Test Title", user=mock_user)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check user name link (should have @ removed)
    user_name_link = soup.select_one(".user-name")
    assert user_name_link is not None
    assert user_name_link.text == "TestUser"  # @ should be removed


def test_create_base_document_with_additional_kwargs():
    """Test base document creation with additional kwargs passed to content_func."""

    # Arrange
    def content_function(test_param=None):
        from dominate.tags import div
        from dominate.tags import p

        with div(cls="test-content"):
            p(f"Test param: {test_param}")

    # Act
    document = create_base_document(
        title_text="Test Title", content_func=content_function, test_param="Hello World"
    )

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check content with passed parameter
    content_div = soup.select_one(".test-content")
    assert content_div is not None
    assert content_div.select_one("p").text == "Test param: Hello World"
