from bs4 import BeautifulSoup

from backend.dominate_templates.components.pagination import create_pagination


def render_pagination_to_soup(count, limit, offset, base_url):
    """Helper function to render pagination and parse with BeautifulSoup."""
    from dominate.document import document

    doc = document()
    with doc:
        create_pagination(count=count, limit=limit, offset=offset, base_url=base_url)

    html_content = doc.render()
    return BeautifulSoup(html_content, "html.parser")


def test_pagination_single_page():
    """Test that pagination is not rendered when there's only one page."""
    # Arrange & Act
    from dominate.document import document

    doc = document()
    with doc:
        create_pagination(count=5, limit=10, offset=0, base_url="/test/")

    # Assert
    html_content = doc.render()
    soup = BeautifulSoup(html_content, "html.parser")

    # No pagination should be rendered
    pagination = soup.select(".pagination")
    assert len(pagination) == 0


def test_pagination_multiple_pages():
    """Test pagination with multiple pages."""
    # Arrange & Act
    soup = render_pagination_to_soup(count=30, limit=10, offset=0, base_url="/test/")

    # Assert
    pagination = soup.select_one(".pagination")
    assert pagination is not None

    # Should have 5 items: Previous, 1, 2, 3, Next
    page_items = pagination.select("li.page-item")
    assert len(page_items) == 5

    # First page should be active
    active_page = pagination.select_one("li.page-item.active")
    assert active_page is not None
    assert active_page.select_one("a").text == "1"

    # Previous should be disabled
    prev_button = pagination.select("li.page-item")[0]
    assert "disabled" in prev_button["class"]

    # Next should be enabled
    next_button = pagination.select("li.page-item")[-1]
    assert "disabled" not in next_button["class"]

    # Next link should point to offset=10
    next_link = next_button.select_one("a")
    assert "offset=10" in next_link["href"]


def test_pagination_middle_page():
    """Test pagination when on a middle page."""
    # Arrange & Act
    soup = render_pagination_to_soup(count=50, limit=10, offset=20, base_url="/test/")

    # Assert
    pagination = soup.select_one(".pagination")
    assert pagination is not None

    # Current page should be 3
    active_page = pagination.select_one("li.page-item.active")
    assert active_page is not None
    assert active_page.select_one("a").text == "3"

    # Both Previous and Next should be enabled
    prev_button = pagination.select("li.page-item")[0]
    assert "disabled" not in prev_button["class"]

    next_button = pagination.select("li.page-item")[-1]
    assert "disabled" not in next_button["class"]

    # Previous link should point to offset=10
    prev_link = prev_button.select_one("a")
    assert "offset=10" in prev_link["href"]

    # Next link should point to offset=30
    next_link = next_button.select_one("a")
    assert "offset=30" in next_link["href"]


def test_pagination_last_page():
    """Test pagination when on the last page."""
    # Arrange & Act
    soup = render_pagination_to_soup(count=30, limit=10, offset=20, base_url="/test/")

    # Assert
    pagination = soup.select_one(".pagination")
    assert pagination is not None

    # Current page should be 3
    active_page = pagination.select_one("li.page-item.active")
    assert active_page is not None
    assert active_page.select_one("a").text == "3"

    # Previous should be enabled
    prev_button = pagination.select("li.page-item")[0]
    assert "disabled" not in prev_button["class"]

    # Next should be disabled
    next_button = pagination.select("li.page-item")[-1]
    assert "disabled" in next_button["class"]


def test_pagination_many_pages():
    """Test pagination with many pages shows limited page numbers."""
    # Arrange & Act
    soup = render_pagination_to_soup(count=100, limit=10, offset=30, base_url="/test/")

    # Assert
    pagination = soup.select_one(".pagination")
    assert pagination is not None

    # Should have 7 items: Previous, 2, 3, 4, 5, 6, Next
    # (5 page numbers + Previous + Next)
    page_items = pagination.select("li.page-item")
    assert len(page_items) == 7

    # Current page should be 4
    active_page = pagination.select_one("li.page-item.active")
    assert active_page is not None
    assert active_page.select_one("a").text == "4"

    # Check the range of page numbers
    page_numbers = [
        item.select_one("a").text
        for item in pagination.select("li.page-item")
        if item.select_one("a").text not in ["Previous", "Next"]
    ]
    assert page_numbers == ["2", "3", "4", "5", "6"]


def test_pagination_near_end():
    """Test pagination when near the end shows correct range."""
    # Arrange & Act
    soup = render_pagination_to_soup(count=100, limit=10, offset=80, base_url="/test/")

    # Assert
    pagination = soup.select_one(".pagination")
    assert pagination is not None

    # Current page should be 9
    active_page = pagination.select_one("li.page-item.active")
    assert active_page is not None
    assert active_page.select_one("a").text == "9"

    # Check the range of page numbers
    page_numbers = [
        item.select_one("a").text
        for item in pagination.select("li.page-item")
        if item.select_one("a").text not in ["Previous", "Next"]
    ]
    assert page_numbers == ["6", "7", "8", "9", "10"]


def test_pagination_base_url_with_query_params():
    """Test pagination with base URL that already has query parameters."""
    # Arrange & Act
    soup = render_pagination_to_soup(
        count=30, limit=10, offset=10, base_url="/test/?filter=active"
    )

    # Assert
    pagination = soup.select_one(".pagination")
    assert pagination is not None

    # Check that links have both the original query param and pagination params
    next_link = pagination.select("li.page-item")[-1].select_one("a")["href"]
    assert next_link.startswith("/test/?filter=active")
    assert "limit=10" in next_link
    assert "offset=20" in next_link


def test_pagination_custom_limit():
    """Test pagination with custom limit value."""
    # Arrange & Act
    soup = render_pagination_to_soup(count=60, limit=15, offset=15, base_url="/test/")

    # Assert
    pagination = soup.select_one(".pagination")
    assert pagination is not None

    # Current page should be 2
    active_page = pagination.select_one("li.page-item.active")
    assert active_page is not None
    assert active_page.select_one("a").text == "2"

    # Check that links use the custom limit
    next_link = pagination.select("li.page-item")[-1].select_one("a")["href"]
    assert "limit=15" in next_link
    assert "offset=30" in next_link
