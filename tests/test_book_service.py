import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from app.exceptions import ServiceException
from app.services.book_service import BookService
from app.models.book import BookInfo, Book
from app.models.review import ReviewInfo

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def book_service(mock_db):
    return BookService(db=mock_db)

def test_get_books_returns_list(book_service, mock_db):
    # 1) Arrange
    # Mock the query so that calling .all() returns a list of Book objects
    # Python's unittest.mock library enables dynamic attribute creation
    # When you access any attribute on a Mock object that hasn't been defined, 
    # it automatically generates a new Mock object for that attribute
    mock_db.query.return_value.all.return_value = [
        Book(id=1, title="Title1", author="Author1", year=2021, description="Desc1"),
        Book(id=2, title="Title2", author="Author2", year=2022, description="Desc2"),
    ]

    # 2) Act
    books = book_service.get_books()

    # 3) Assert
    assert len(books) == 2
    assert books[0].title == "Title1"
    assert books[1].title == "Title2"
    # Ensure the correct calls were made
    mock_db.query.assert_called_once_with(Book)
    mock_db.query.return_value.all.assert_called_once()

def test_create_duplicate_book(book_service, mock_db):
    book_data = BookInfo(title="Test Book", author="Test Author", year=2021, description="Test Description")
    existing_book = Mock()
    existing_book.title = book_data.title
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_book
    
    with pytest.raises(ServiceException) as exc_info:
        book_service.add_book(book_data)
    
    assert exc_info.value.status_code == 409
    assert "Book with this title already exists" in exc_info.value.detail
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

def test_title_exists_case_insensitive(book_service, mock_db):
    existing_book = Mock()
    existing_book.title = "Test Book"
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_book
    
    book_data = BookInfo(title="TEST BOOK", author="Test Author", year=2021, description="Test Description")

    with pytest.raises(ServiceException) as exc_info:
        book_service.add_book(book_data)
    
    assert exc_info.value.status_code == 409

def test_add_new_book(book_service, mock_db):
    book_data = BookInfo(title="New Book", author="New Author", year=2022, description="New Description")
    
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    new_book = Mock()
    new_book.id = 1
    new_book.title = book_data.title
    new_book.author = book_data.author
    new_book.year = book_data.year
    new_book.description = book_data.description

    mock_db.add.return_value = new_book
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = new_book
    
    result = book_service.add_book(book_data)
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result.title == book_data.title

def test_update_book(book_service, mock_db):
    book_id = 1
    existing_book = Mock()
    existing_book.id = book_id
    updated_data = BookInfo(title="Updated Book", author="Updated Author", year=2023, description="Updated Description")
    
    # side_effect usage:
    # The first time first() is called, it will return the existing_book object
    # The second time first() is called, it will return None
    mock_db.query.return_value.filter.return_value.first.side_effect = [existing_book, None]
    
    result = book_service.update_book(book_id, updated_data)
    
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result == existing_book

def test_delete_book(book_service, mock_db):
    book_id = 1
    existing_book = Mock()
    existing_book.id = book_id
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_book
    
    result = book_service.delete_book(book_id)
    
    mock_db.delete.assert_called_once_with(existing_book)
    mock_db.commit.assert_called_once()
    assert result is True

def test_delete_nonexistent_book(book_service, mock_db):
    book_id = 1
    
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    
    result = book_service.delete_book(book_id)
    
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()
    assert result is False
    
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


def test_count_longest_titles_one_longest_return1(book_service, mock_db):
    # 1) Arrange
    # Prepare a mock 'books' repository that returns a specific list of Book objects
    mock_db.query.return_value.all.return_value = [
        Book(title="The Longest"),
        Book(title="The Longest Title"),
        Book(title="The Longest Title of Book"),
    ]

    # 2) Act
    count = book_service.count_longest_book_titles()

    # 3) Assert
    assert count == 1
    mock_db.query.assert_called_once()


def test_count_longest_titles_two_longest_return2(book_service, mock_db):
    # 1) Arrange
    mock_db.query.return_value.all.return_value = [
        Book(title="The Longest"),
        Book(title="The Longer Title of Book"),
        Book(title="The Longest"),
        Book(title="The Longest Title of Book"),
    ]

    # 2) Act
    count = book_service.count_longest_book_titles()

    # 3) Assert
    assert count == 2
    mock_db.query.assert_called_once()


def test_count_longest_titles_all_longest_return4(book_service, mock_db):
    # 1) Arrange
    mock_db.query.return_value.all.return_value = [
        Book(title="The Long Book"),
        Book(title="The Longer Book"),
        Book(title="The Longerer Book"),
        Book(title="The Longest Book"),
    ]

    # 2) Act
    count = book_service.count_longest_book_titles()

    # 3) Assert
    assert count == 4
    mock_db.query.assert_called_once()


def test_get_most_common_words_in_titles_return_empty_map(book_service, mock_db):
    """
    If we pass in top_k=0, we expect an empty dictionary returned.
    """
    # 1) Arrange
    # Mock that .all() returns any list of books, 
    # but top_k=0 => empty dict anyway
    mock_db.query.return_value.all.return_value = [
        Book(title="Some Book"),
        Book(title="Another Title")
    ]
    book_service = BookService(mock_db)

    # 2) Act
    actual = book_service.get_most_common_words_in_titles(0)

    # 3) Assert
    expected = {}
    assert actual == expected
    mock_db.assert_not_called()

def test_get_most_common_words_in_titles_sort_by_word_count(book_service, mock_db):
    # 1) Arrange
    mock_db.query.return_value.all.return_value = [
        Book(title="Book book book"),
        Book(title="Title title"),
        Book(title="Word word word word")
    ]
    book_service = BookService(mock_db)

    # 2) Act
    actual = book_service.get_most_common_words_in_titles(2)

    # 3) Assert
    # In these titles:
    #  - "book" appears 3 times
    #  - "word" appears 4 times
    #  - "title" appears 2 times
    # The top-2 by frequency: word(4), book(3)
    # Return them in a dict: {"word": 4, "book": 3}
    # Then check that the code returns exactly that.
    expected = {"word": 4, "book": 3}
    assert actual == expected

    mock_db.query.assert_called_once()