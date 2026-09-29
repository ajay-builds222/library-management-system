from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book
from app.models.category import Category
from app.schemas.book import BookCreate, BookResponse

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    existing = db.query(Book).filter(Book.isbn == book.isbn).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="ISBN already exists"
        )

    category = db.query(Category).filter(
        Category.id == book.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    if book.total_copies < 0 or book.available_copies < 0:
        raise HTTPException(
            status_code=400,
            detail="Copies cannot be negative"
        )

    if book.available_copies > book.total_copies:
        raise HTTPException(
            status_code=400,
            detail="Available copies cannot exceed total copies"
        )

    new_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        category_id=book.category_id,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        published_year=book.published_year
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book

@router.get("/", response_model=list[BookResponse])
def get_books(
    skip: int = 0,
    limit: int = 10,
    title: str | None = None,
    author: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))

    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))

    if category_id:
        query = query.filter(Book.category_id == category_id)

    books = query.offset(skip).limit(limit).all()

    return books

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return book

@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book: BookCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Book).filter(Book.id == book_id).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    duplicate = db.query(Book).filter(
        Book.isbn == book.isbn,
        Book.id != book_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="ISBN already exists"
        )

    category = db.query(Category).filter(
        Category.id == book.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    if book.total_copies < 0 or book.available_copies < 0:
        raise HTTPException(
            status_code=400,
            detail="Copies cannot be negative"
        )

    if book.available_copies > book.total_copies:
        raise HTTPException(
            status_code=400,
            detail="Available copies cannot exceed total copies"
        )

    existing.title = book.title
    existing.author = book.author
    existing.isbn = book.isbn
    existing.category_id = book.category_id
    existing.total_copies = book.total_copies
    existing.available_copies = book.available_copies
    existing.published_year = book.published_year

    db.commit()
    db.refresh(existing)

    return existing

@router.delete("/{book_id}", status_code=200)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    active_borrow = any(
        borrow.status in ["Borrowed", "Overdue"]
        for borrow in book.borrow_records
    )

    if active_borrow:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a book that is currently borrowed"
        )

    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully"}