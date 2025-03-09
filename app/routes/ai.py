from fastapi import APIRouter, HTTPException, Path, Depends
from dotenv import load_dotenv
from app.services.book_service import BookService
from app.dependencies.services import get_book_service
import openai
import os

load_dotenv()

# Access the OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found. Ensure it is set in the .env file.")

router = APIRouter()

@router.get("/introduction/{book_id}", response_model=dict)
def introduce_book(book_id: int = Path(..., title="The ID of the book to introduce"), 
                   book_service: BookService = Depends(get_book_service),):
    """
    Generate an introduction for a book using OpenAI's text-generation API.
    """
    # Get the book details from the database
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Construct a prompt for OpenAI
    prompt = (
        f"Introduce the book '{book.title}' by {book.author}, published in {book.year}. "
        f"Here is the description: {book.description or 'No description available'}."
    )
    
    # Call OpenAI API
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        client = openai.Client()
 
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a book reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        introduction = completion.choices[0].message.content
        return {"book_id": book_id, "introduction": introduction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
