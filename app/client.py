import requests

BASE_URL = "http://localhost:8000/books"


def get_books():
    """
    Fetch all books from the web service.
    """
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        books = response.json()
        print("[GET] Books:")
        for book in books:
            print(f" - {book['title']}")
        return books
    else:
        print(f"[GET] Failed to fetch books: {response.status_code}")
        return None


def get_book(book_id):
    """
    Fetch a single book by its ID.
    """
    response = requests.get(f"{BASE_URL}/{book_id}")
    if response.status_code == 200:
        book = response.json()
        print(f"[GET] Book {book_id}: {book['title']}")
        return book
    else:
        print(f"[GET] Failed to fetch book {book_id}: {response.status_code}")
        return None


# def add_book(new_book):
#     """
#     Add a new book using a POST request.
#     """
#     response = requests.post(BASE_URL, json=new_book)
#     if response.status_code == 200:
#         book = response.json()
#         print(f"[POST] Book added: {book['title']}")
#         return book
#     else:
#         print(f"[POST] Failed to add book: {response.status_code}")
#         return None


if __name__ == "__main__":
    # Fetch all books
    books = get_books()

    # Fetch a specific book
    if books:
        first_book_id = books[0]["id"]
        get_book(first_book_id)

    # # Add a new book
    # new_book_data = {
    #     "title": "Gone With The Wind",
    #     "author": "Margaret Mitchell",
    #     "year": 1936,
    #     "description": "A historical novel about the American South during the Civil War."
    # }
    # add_book(new_book_data)
