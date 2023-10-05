from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {'id': 1, 'title': 'title 1', 'auther': 'auther1'},
    {'id': 2, 'title': 'title2', 'auther': 'auther2'},
    {'id': 3, 'title': 'title3', 'auther': 'auther3'},
    {'id': 4, 'title': 'title4', 'auther': 'auther3'},
    {'id': 5, 'title': 'title5', 'auther': 'auther2'},
]


# optional query variable example
@app.get("/books")
async def get_all_books(auther: str = None):
    # optional query parameter(auther)
    books_to_return = []
    if auther:
        for book in BOOKS:
            if book.get('auther').casefold() == auther.casefold():
                books_to_return.append(book)
        return books_to_return
    else:
        return BOOKS


# path variable example of string type
@app.get("/books/title/{title}")
async def get_book_by_title(title: str):
    for book in BOOKS:
        if book.get('title').casefold() == title.casefold():
            return book


# path variable example of int type
@app.get("/books/id/{book_id}")
async def get_book_by_id(book_id: int):
    for book in BOOKS:
        if book.get('id') == book_id:
            return book


@app.post("/books/add")
async def add_book(new_book=Body()):
    BOOKS.append(new_book)


@app.put("/books/update/{book_id}")
async def update_book(book_id: int, book_details=Body()):
    for book in BOOKS:
        if book.get('id') == book_id:
            book['title'] = book_details.get('title')
            book['auther'] = book_details.get('auther')
            return book

@app.delete("/books/delete/{book_id}")
async def delete_book(book_id: int):
    for book in BOOKS:
        if book.get('id') == book_id:
            BOOKS.remove(book)
