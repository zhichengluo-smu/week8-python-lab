from fastapi import APIRouter, HTTPException, status
from app.services.chroma_service import ChromaService
from app.models.book import ChromaBookInfo


router = APIRouter()
chroma_service = ChromaService()

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_book_to_chromadb(book: ChromaBookInfo):
    """
    Add a book's title and description to ChromaDB for embedding.
    """
    chroma_service.add_book(book.id, book.title, book.description)
    return {"message": f"Book '{book.title}' added to ChromaDB successfully."}

@router.get("/similarities")
def search_books_in_chromadb(query: str, distance_threshold: float = 1.0):
    """
    Search for similar books in ChromaDB based on a query and a distance_threshold.
    """
    results = chroma_service.search_books(query, distance_threshold=distance_threshold)
    if not results:
        raise HTTPException(status_code=404, detail=f"No similar books found for the query: '{query}'.")

    return {"query": query, "response": results}


@router.get("/summary")
def ai_search_books_in_chromadb(query: str, distance_threshold: float = 1.0):
    """
    Search for similar books in ChromaDB based on a query and return a natural language summary using OpenAI.
    """
    results = chroma_service.search_books(query, distance_threshold=distance_threshold)
    if not results:
        raise HTTPException(status_code=404, detail=f"No similar books found for the query: '{query}'.")

    # Generate a natural language response using OpenAI
    response = chroma_service.generate_natural_language_response(query, results)
    return {"query": query, "response": response}

@router.delete("/{book_id}")
def delete_book(book_id: str):
    """
    Delete a book's vector and metadata from ChromaDB by its ID.
    """
    chroma_service.collection.delete(ids=[book_id])
    return {"message": f"Book with ID '{book_id}' deleted from ChromaDB successfully."}

