import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.book import Base, BookInfo
from app.dependencies.services import get_db
from app.dependencies.auth import required_admin_role

# Setup the database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Mock security dependency
def mock_required_admin_role():
    pass

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
    
@pytest.fixture(autouse=True)
def dependency_overrides():
    # Set the dependency override for testing
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[required_admin_role] = mock_required_admin_role
    yield
    # Reset any overrides after the test.
    app.dependency_overrides = {}

# This fixture is used to automatically setup and teardown the database for each test function
@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Setup: Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: Drop tables
    Base.metadata.drop_all(bind=engine)

def test_add_book(client):
    response = client.post("/books/", json={
        "title": "New Book",
        "author": "New Author",
        "year": 2022,
        "description": "New Description"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Book"
    assert data["author"] == "New Author"

def test_get_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_book(client):
    # First, add a book
    response = client.post("/books/", json={
        "title": "New Book",
        "author": "New Author",
        "year": 2022,
        "description": "New Description"
    })
    book_id = response.json()["id"]

    # Then, retrieve the book by ID
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Book"
    assert data["author"] == "New Author"

def test_update_book(client):
    # First, add a book
    response = client.post("/books/", json={
        "title": "Old Book",
        "author": "Old Author",
        "year": 2021,
        "description": "Old Description"
    })
    book_id = response.json()["id"]

    # Then, update the book
    response = client.put(f"/books/{book_id}", json={
        "title": "Updated Book",
        "author": "Updated Author",
        "year": 2023,
        "description": "Updated Description"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Book"
    assert data["author"] == "Updated Author"

def test_delete_book(client):
    # First, add a book
    response = client.post("/books/", json={
        "title": "Book to Delete",
        "author": "Author",
        "year": 2021,
        "description": "Description"
    })
    book_id = response.json()["id"]

    # Then, delete the book
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200

    # Verify the book is deleted
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404