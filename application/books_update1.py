from fastapi import FastAPI, Body, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'tanuj',
                'description': 'Detailed description of a book',
                'rating': 5,
                'published_date': 2029
            }
        }


BOOKS = [
    Book(1, 'Computer Science Pro', 'A new 1', 'A very nice book!', 5, 2030),
    Book(2, 'Be Fast with FastAPI', 'A new 2', 'A great book!', 5, 2030),
    Book(3, 'Master Endpoints', 'A new 33', 'A awesome book!', 5, 2029),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 2028),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 2027),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 2026)
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def get_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Book not found')


@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_books_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_result = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_result.append(book)
    return books_result


def get_book_id(book: Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def add_book(new_book: BookRequest):
    # new_book should be of type class whose base class is BaseModel for validation
    book = Book(**new_book.dict())  # as per version of pydantic if dict() doesn't work, try model_dump()
    book = get_book_id(book)
    BOOKS.append(book)
    return book


@app.put("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
# HTTP_204_NO_CONTENT is suitable when no data is returned in success case
# HTTP_204_NO_CONTENT response does not have a body.
async def update_book_by_id(book_id: int, book_details: BookRequest):
    is_book_updated = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            book = Book(**book_details.dict())
            book.id = book_id
            BOOKS[i] = book
            is_book_updated = True
    if not is_book_updated:
        raise HTTPException(status_code=404, detail='Book not found')


@app.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
# HTTP_204_NO_CONTENT can be used but as object is being returned, so using HTTP_200_OK
async def delete_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            BOOKS.remove(book)
            return book
    raise HTTPException(status_code=404, detail='Book not found')
