from dotenv import load_dotenv
from os import getenv

load_dotenv()

def get_pages_slice(current_page: int, total_pages: int) -> list:
    pages_slice = []
    left_pages = current_page - int(getenv('NUM_PAGES_LEFT_SIDE', 2))
    right_pages = current_page + int(getenv('NUM_PAGES_RIGHT_SIDE', 2)) + 1
    for page_num in range(left_pages, right_pages):
        if page_num in range(1, total_pages + 1):
            pages_slice.append(str(page_num))
    return pages_slice