"""Module with functions for work with pages."""

from os import getenv

from dotenv import load_dotenv

load_dotenv()


def get_pages_slice(current_page: int, total_pages: int) -> list:
    """Get list with numbers of pages near current page.

    Args:
        current_page: int - number of current page.
        total_pages: int - pages total count.

    Returns:
        list: pages numbers.
    """
    pages_slice = []
    left_pages = current_page - int(getenv('NUM_PAGES_LEFT_SIDE', 2))
    right_pages = current_page + int(getenv('NUM_PAGES_RIGHT_SIDE', 2)) + 1
    for page_num in range(left_pages, right_pages):
        if page_num in range(1, total_pages + 1):
            pages_slice.append(str(page_num))
    return pages_slice
