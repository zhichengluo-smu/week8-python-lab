from sqlalchemy import Column, Integer, String
from app.db.db import Base
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import relationship

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    description = Column(String, nullable=True)

    # Relationship with reviews
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    
# Pydantic Models for Request/Response
class BookBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="The title of the book (3-100 characters)")
    author: str = Field(..., min_length=3, max_length=50, description="The author of the book (3-50 characters)")
    year: int = Field(..., gt=0, description="The publication year of the book (must be positive)")
    description: str = Field(..., min_length=10, max_length=1000, description="The description of the book (10-1000 characters)")

class BookInfo(BookBase):
    pass

class ChromaBookInfo(BaseModel):
    id: str
    title: str
    description: str | None = None

class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)
    id: int