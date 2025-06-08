from dominate.tags import a
from dominate.tags import li
from dominate.tags import nav
from dominate.tags import ul


def create_pagination(
    count: int,
    limit: int,
    offset: int,
    base_url: str,
) -> None:
    """
    Create a pagination component.

    Args:
        count: Total number of items
        limit: Number of items per page
        offset: Current offset
        base_url: Base URL for pagination links
    """
    total_pages = (count + limit - 1) // limit
    current_page = offset // limit + 1

    # Don't show pagination if there's only one page
    if total_pages <= 1:
        return

    with nav(aria_label="Page navigation"), ul(cls="pagination"):  # type: ignore
        # Previous page button
        with li(cls=f"page-item {'disabled' if current_page == 1 else ''}"):  # type: ignore
            if current_page > 1:
                prev_offset = max(0, offset - limit)
                a(
                    "Previous",
                    href=f"{base_url}?limit={limit}&offset={prev_offset}",
                    cls="page-link",
                )  # type: ignore
            else:
                a(
                    "Previous",
                    href="#",
                    cls="page-link",
                    tabindex="-1",
                    aria_disabled="true",
                )  # type: ignore

        # Page numbers
        max_pages_to_show = 5
        start_page = max(1, current_page - max_pages_to_show // 2)
        end_page = min(total_pages, start_page + max_pages_to_show - 1)

        # Adjust start_page if we're near the end
        if end_page == total_pages:
            start_page = max(1, end_page - max_pages_to_show + 1)

        for page_num in range(start_page, end_page + 1):
            page_offset = (page_num - 1) * limit
            is_current = page_num == current_page

            with li(cls=f"page-item {'active' if is_current else ''}"):  # type: ignore
                if is_current:
                    a(
                        str(page_num),
                        href="#",
                        cls="page-link",
                        aria_current="page",
                    )  # type: ignore
                else:
                    a(
                        str(page_num),
                        href=f"{base_url}?limit={limit}&offset={page_offset}",
                        cls="page-link",
                    )  # type: ignore

        # Next page button
        with li(cls=f"page-item {'disabled' if current_page >= total_pages else ''}"):  # type: ignore
            if current_page < total_pages:
                next_offset = offset + limit
                a(
                    "Next",
                    href=f"{base_url}?limit={limit}&offset={next_offset}",
                    cls="page-link",
                )  # type: ignore
            else:
                a(
                    "Next",
                    href="#",
                    cls="page-link",
                    tabindex="-1",
                    aria_disabled="true",
                )  # type: ignore
