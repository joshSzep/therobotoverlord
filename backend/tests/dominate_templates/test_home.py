from datetime import datetime
from unittest import mock
import uuid

from bs4 import BeautifulSoup
import pytest

from backend.dominate_templates.home import create_home_page
from backend.routes.html.schemas.user import UserResponse
from backend.schemas.post import PostResponse
from backend.schemas.topic import TopicResponse


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = mock.MagicMock(spec=UserResponse)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.is_admin = False
    user.approved_count = 5
    user.rejected_count = 2
    return user


@pytest.fixture
def mock_topics():
    """Create mock topics for testing."""
    topics = []
    for i in range(3):
        topic = mock.MagicMock(spec=TopicResponse)
        topic.id = uuid.uuid4()
        topic.title = f"Test Topic {i + 1}"
        topic.description = f"Description for topic {i + 1}"
        topic.post_count = i + 5
        topic.tags = []
        for j in range(2):
            tag = mock.MagicMock()
            tag.name = f"tag{j + 1}"
            topic.tags.append(tag)
        topics.append(topic)
    return topics


@pytest.fixture
def mock_posts(mock_user, mock_topics):
    """Create mock posts for testing."""
    posts = []
    for i in range(3):
        post = mock.MagicMock(spec=PostResponse)
        post.id = uuid.uuid4()
        post.title = f"Test Post {i + 1}"
        post.content = f"This is the content for post {i + 1}. " * 5
        post.author = mock_user
        post.topic_id = mock_topics[i % len(mock_topics)].id
        post.created_at = datetime.now()
        posts.append(post)
    return posts


def test_create_home_page_with_user_topics_and_posts(
    mock_user, mock_topics, mock_posts
):
    """Test home page creation with authenticated user, topics, and posts."""
    # Arrange & Act
    document = create_home_page(topics=mock_topics, posts=mock_posts, user=mock_user)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check page title
    assert soup.title.text == "The Robot Overlord - Home"

    # Check home banner
    banner = soup.select_one(".home-banner")
    assert banner is not None
    assert banner.select_one("h1").text == "WELCOME, CITIZEN"

    # Check topics section
    topics_section = soup.select_one(".featured-topics")
    assert topics_section is not None
    assert topics_section.select_one("h2").text == "APPROVED TOPICS FOR DISCUSSION"

    # Check that all topics are displayed
    topic_elements = topics_section.select(".topic")
    assert len(topic_elements) == len(mock_topics)

    # Check first topic content
    first_topic = topic_elements[0]
    assert mock_topics[0].title in first_topic.select_one("h3 a").text
    assert mock_topics[0].description in first_topic.select_one("p").text
    assert (
        f"{mock_topics[0].post_count} posts"
        in first_topic.select_one(".topic-meta").text
    )

    # Check topic tags
    topic_tags = first_topic.select(".topic-tags .tag")
    assert len(topic_tags) == len(mock_topics[0].tags)

    # Check posts section
    posts_section = soup.select_one(".recent-posts")
    assert posts_section is not None
    assert posts_section.select_one("h2").text == "RECENT CONTRIBUTIONS"

    # Check that all posts are displayed
    post_elements = posts_section.select(".post")
    assert len(post_elements) == len(mock_posts)

    # Check first post content
    first_post = post_elements[0]
    assert mock_posts[0].title in first_post.select_one("h3 a").text
    assert mock_posts[0].content[:50] in first_post.select_one("p").text

    # Check post author info
    author_link = first_post.select_one(".user-info a")
    assert author_link is not None
    assert mock_user.display_name in author_link.text
    assert f"/html/profile/{mock_user.id}/" in author_link["href"]

    # Check post stats
    stats = first_post.select(".user-info .stats span")
    assert len(stats) == 2
    assert f"✓ {mock_user.approved_count}" in stats[0].text
    assert f"✗ {mock_user.rejected_count}" in stats[1].text


def test_create_home_page_without_user(mock_topics, mock_posts):
    """Test home page creation without authenticated user."""
    # Arrange & Act
    document = create_home_page(topics=mock_topics, posts=mock_posts, user=None)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check that the page renders without user
    assert soup.title.text == "The Robot Overlord - Home"

    # Check that the login link is present in the header
    header = soup.select_one(".site-header")
    assert header is not None
    login_link = header.select_one(".user-info a")
    assert login_link is not None
    assert login_link.text == "CITIZEN"
    assert login_link["href"] == "/html/auth/login/"


def test_create_home_page_without_topics(mock_user, mock_posts):
    """Test home page creation without topics."""
    # Arrange & Act
    document = create_home_page(topics=[], posts=mock_posts, user=mock_user)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check topics section empty message
    topics_section = soup.select_one(".featured-topics")
    assert topics_section is not None
    assert (
        "NO TOPICS HAVE BEEN APPROVED BY THE CENTRAL COMMITTEE" in topics_section.text
    )

    # Topic grid should not exist
    topic_grid = topics_section.select_one(".topics-grid")
    assert topic_grid is None


def test_create_home_page_without_posts(mock_user, mock_topics):
    """Test home page creation without posts."""
    # Arrange & Act
    document = create_home_page(topics=mock_topics, posts=[], user=mock_user)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check posts section empty message
    posts_section = soup.select_one(".recent-posts")
    assert posts_section is not None
    assert "NO RECENT POSTS HAVE BEEN APPROVED" in posts_section.text

    # Posts list should not exist
    posts_list = posts_section.select_one(".posts-list")
    assert posts_list is None


def test_create_home_page_long_post_content(mock_user, mock_topics):
    """Test home page with long post content that should be truncated."""
    # Arrange
    long_content = "This is a very long post content that should be truncated. " * 10

    post = mock.MagicMock(spec=PostResponse)
    post.id = uuid.uuid4()
    post.title = "Long Content Post"
    post.content = long_content
    post.author = mock_user
    post.topic_id = mock_topics[0].id
    post.created_at = datetime.now()

    # Act
    document = create_home_page(topics=mock_topics, posts=[post], user=mock_user)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check that post content is truncated
    post_content = soup.select_one(".post p").text
    assert len(post_content) <= 150
    assert post_content.endswith("...")
    assert post_content == long_content[:147] + "..."


def test_create_home_page_topic_link_in_post(mock_user, mock_topics):
    """Test that posts correctly link to their topics."""
    # Arrange
    post = mock.MagicMock(spec=PostResponse)
    post.id = uuid.uuid4()
    post.title = "Test Post"
    post.content = "Test content"
    post.author = mock_user
    post.topic_id = mock_topics[0].id
    post.created_at = datetime.now()

    # Act
    document = create_home_page(topics=mock_topics, posts=[post], user=mock_user)

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check that post links to correct topic
    post_meta = soup.select_one(".post-meta")
    topic_link = post_meta.select_one("a")
    assert topic_link is not None
    assert topic_link.text == mock_topics[0].title
    assert f"/html/topics/{mock_topics[0].id}/" in topic_link["href"]


def test_create_home_page_with_topic_without_tags(mock_user, mock_posts):
    """Test home page with topics that don't have tags."""
    # Arrange
    topic_without_tags = mock.MagicMock(spec=TopicResponse)
    topic_without_tags.id = uuid.uuid4()
    topic_without_tags.title = "Topic Without Tags"
    topic_without_tags.description = "This topic has no tags"
    topic_without_tags.post_count = 3
    topic_without_tags.tags = []

    # Act
    document = create_home_page(
        topics=[topic_without_tags], posts=mock_posts, user=mock_user
    )

    # Assert
    html_content = document.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # Check that topic renders correctly without tags
    topic = soup.select_one(".topic")
    assert topic is not None

    # Topic tags section should not exist or be empty
    topic_tags = topic.select(".topic-tags .tag")
    assert len(topic_tags) == 0
