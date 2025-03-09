from fastapi import APIRouter, Depends, HTTPException, status
from app.models.review import ReviewInfo, ReviewResponse
from app.services.review_service import ReviewService
from app.dependencies.services import get_review_service
from app.models.book import Book
from app.models.review import Review

from app.dependencies.auth import required_user_role

router = APIRouter()

@router.get("/books/{book_id}/reviews", response_model=list[ReviewResponse])
def get_reviews(
    book_id: int,
    service: ReviewService = Depends(get_review_service)
):
    reviews = service.get_reviews_by_book_id(book_id)
    if not reviews:
        raise HTTPException(status_code=404, detail=f"No reviews found for book {book_id}")
    return reviews

@router.get("/books/{book_id}/reviews/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    service: ReviewService = Depends(get_review_service)
):
    review = service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"No review found with id {review_id}")
    return review

@router.post("/books/{book_id}/reviews", 
             response_model=ReviewResponse, 
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(required_user_role)],
             )  
def add_review(
    book_id: int,
    review: ReviewInfo,
    service: ReviewService = Depends(get_review_service),
):
    
    new_review = service.add_review(book_id, review)
    if not new_review:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return new_review

@router.put("/books/{book_id}/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    book_id: int,
    review_id: int,
    new_review: ReviewInfo,
    service: ReviewService = Depends(get_review_service),
):
    updated_review = service.update_review(book_id, review_id, new_review)
    if not updated_review:
        raise HTTPException(status_code=404, detail=f"Review with id {review_id} for book {book_id} not found")
    return updated_review

@router.delete("/books/{book_id}/reviews/{review_id}")
def delete_review(
    book_id: int,
    review_id: int,
    service: ReviewService = Depends(get_review_service),
):
    success = service.delete_review(book_id, review_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Review with id {review_id} for book {book_id} not found")
    return {"message": "Review deleted successfully"}