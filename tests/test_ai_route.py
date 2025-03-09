import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.models.book import Base, BookInfo
from app.services.book_service import BookService
from app.dependencies.services import get_book_service
from dotenv import load_dotenv
import openai
import os

# skip all AI tests in CI to save OpenAI cost
pytestmark = pytest.mark.skip("Skip AI tests in CI")

@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_book_service():
    # With spec, mock object will only allow attributes and methods that exist in the BookService class
    return Mock(spec=BookService)

@pytest.fixture(autouse=True)
def override_book_service(mock_book_service):
    app.dependency_overrides[get_book_service] = lambda: mock_book_service
    yield
    # reset dependency overrides after the test
    app.dependency_overrides = {}

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found. Ensure it is set in the .env file.")

def test_get_introduction(client, mock_book_service):
    mock_book = Mock()
    book_id = 1
    mock_book.book_id = book_id
    mock_book.title = "FastAPI: Modern Python Web Development"
    mock_book.author = "Bill Lubanovic"
    mock_book.year = 2023
    mock_book.description = "With this practical book, developers familiar with Python will learn how FastAPI lets you accomplish more in less time with less code."
    mock_book_service.get_book.return_value = mock_book
    
    response = client.get(f"/ai/introduction/{book_id}")
    
    intro = response.json()["introduction"]
    
    test_prompt = (
        f"Given the book '{mock_book.title}' by {mock_book.author}. "
        f"Here is the description of the book: {mock_book.description}. "
        f"The book was published in {mock_book.year}. "
        f"Please provide a rating for the following introduction of the book: {intro}. " 
        f"The rating should be from 1 (not appropriate) to 5 (very appropriate)."
        f"Return only the numeric value of the rating."
    )

    # Call OpenAI API
    openai.api_key = os.getenv("OPENAI_API_KEY")
    client = openai.Client()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are to rate book introductions."},
            {"role": "user", "content": test_prompt}
        ],
        # Set temperature to 0 for more deterministic output
        temperature=0,
        max_completion_tokens=2048,
        frequency_penalty=0,
        presence_penalty=0,
    )
    rating = completion.choices[0].message.content
    assert rating in ["4", "5"]
    