from typing import Counter, Dict, OrderedDict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.exceptions import ServiceException
from app.models.book import Book, BookInfo

class BookService:
    def __init__(self, db: Session):
        self.db = db

    def get_books(self):
        """Retrieve all books."""
        return self.db.query(Book).all()

    def get_book(self, book_id: int):
        """Retrieve a book by ID."""
        return self.db.query(Book).filter(Book.id == book_id).first()
    
    def add_book(self, book_data: BookInfo):
        """Add a new book."""
        new_book = Book(**book_data.model_dump())

        # check if book already exists
        existing_book = self.db.query(Book).filter(func.lower(Book.title) == func.lower(new_book.title)).first()
        if existing_book:
            raise ServiceException(status_code=409, detail="Book with this title already exists")
        
        self.db.add(new_book)
        self.db.commit()
        self.db.refresh(new_book)
        return new_book

    def update_book(self, book_id: int, updated_data: BookInfo):
        """Update an existing book."""
        book = self.get_book(book_id)
        if not book:
            return None
                
        existing_book = self.db.query(Book).filter(func.lower(Book.title) == func.lower(updated_data.title)).first()
        if existing_book and existing_book.id != book_id:
            raise ServiceException(status_code=409, detail="Book with this title already exists")
        
        for key, value in updated_data.model_dump().items():
            setattr(book, key, value)
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete_book(self, book_id: int):
        """Delete a book by ID."""
        book = self.get_book(book_id)
        if not book:
            return False
        self.db.delete(book)
        self.db.commit()
        return True
    
    def count_longest_book_titles(self) -> int:
        # Assume that book titles contain only alphabets and whitespaces
        all_books = self.get_books()
        selected_books = []
        
        count=0
        longest_title = 0
        # First pass: find the maximum word count
        for book in all_books:
            s = book.title
            charcount = len(s)

            count = 0
            found = False
            eol = len(s) - 1

            for i in range(len(s)):
                if i != eol and s[i].isalpha():
                    found = True
                elif (not s[i].isalpha()) and found:
                    count += 1
                    found = False
                elif s[i].isalpha() and i == eol:
                    count += 1
            
            print(charcount)
            if count > longest_title:
                longest_title = count

        count1 = 0
        # Second pass: count how many match that longest word count
        for book in all_books:
            s = book.title

            count = 0
            found = False
            eol = len(s) - 1

            for i in range(len(s)):
                if i != eol and s[i].isalpha():
                    found = True
                elif (not s[i].isalpha()) and found:
                    count += 1
                    found = False
                elif s[i].isalpha() and i == eol:
                    count += 1

            if count == longest_title:
                count1 += 1

        return count1

    # def _count_words_in_title(self, title: str) -> int:
    #     """
    #     Private helper: returns the word count for a given title.
    #     """
    #     return len(title.split())
    
    # def _get_longest_title_length(self, books: list) -> int:
    #     """
    #     Private helper: determines the max word count among all titles in `books`.
    #     """
    #     return max((self._count_words_in_title(book.title) for book in books), default=0)

    # def _count_books_with_word_count(self, books: list, word_count: int) -> int:
    #     """
    #     Private helper: counts how many books in `books` have the specified `word_count`.
    #     """
    #     return sum(1 for book in books if self._count_words_in_title(book.title) == word_count)

    # def count_longest_book_titles(self) -> int:
    #     books = self.get_books()
    #     """
    #     Public method:
    #         1) Determine the word-count of the longest title.
    #         2) Count how many books match that word-count.
    #         3) Return that count.
    #     """
    #     longest_title_length = self._get_longest_title_length(books)
    #     return self._count_books_with_word_count(books, longest_title_length)
    
    def get_most_common_words_in_titles(self, top_k: int) -> Dict[str, int]:
        """
        Example:
          - If there are two books: 
               "I'm a Book", "This book is great"
          - Then get_most_common_words_in_titles(2) might return:
               {"book": 2, "a": 1}
          - get_most_common_words_in_titles(3) might return:
               {"book": 2, "a": 1, "is": 1}

        :param top_k: how many words to return (0 => return empty dict).
        :return: a dictionary of at most top_k words -> count, 
                 sorted by frequency desc, then alphabetically asc.
        """

        # 1) If top_k <= 0, return an empty dict immediately
        if top_k <= 0:
            return {}

        # 2) Fetch all books
        all_books = self.db.query(Book).all()

        # 3) Build a frequency map of all words, ignoring case
        #    We'll use a Counter from the collections module
        word_counter = Counter()

        for book in all_books:
            # Split on whitespace, convert each word to lowercase
            # You may want to strip punctuation or do more advanced logic as needed
            words = book.title.lower().split()
            word_counter.update(words)

        if not word_counter:
            # If no words found at all
            return {}

        # 4) Sort the words by:
        #    (1) frequency (descending), 
        #    (2) alphabetical (ascending)
        # Counter.most_common() only sorts by frequency desc, so we need a custom sort
        sorted_items = sorted(
            word_counter.items(),
            key=lambda x: (-x[1], x[0])  # -x[1] = descending freq, x[0] = alpha asc
        )

        # 5) Take the top_k items from the sorted list
        top_items = sorted_items[:top_k]

        # 6) Convert to a dict, preserving sorted order (use OrderedDict if needed)
        returned_dict = OrderedDict(top_items)

        return dict(returned_dict)


"""
Count the number of books in the database having the longest title length.
A title is a sequence of words separated by whitespace.
The length is the number of words in the title.
"""
def count_longest_book_titles(self) -> int:
    # Fetch all books
    books = self.get_books()# 

    # get the longest title length
    longest_title_length = 0
    for book in books:
        title_length = len(book.title.split())
        longest_title_length = max(longest_title_length, title_length)
