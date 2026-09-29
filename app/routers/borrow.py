from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from app.schemas.borrow import BorrowCreate, BorrowResponse

router = APIRouter(
    prefix="/borrow",
    tags=["Borrow & Return"]
)


@router.post("/", response_model=BorrowResponse, status_code=201)
def borrow_book(
    borrow: BorrowCreate,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.id == borrow.book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    member = db.query(Member).filter(
        Member.id == borrow.member_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )

    if not member.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive member cannot borrow books"
        )

    if book.available_copies <= 0:
        raise HTTPException(
            status_code=400,
            detail="Book is not available"
        )

    active_borrows = db.query(Borrow).filter(
        Borrow.member_id == borrow.member_id,
        Borrow.status.in_(["Borrowed", "Overdue"])
    ).count()

    if active_borrows >= 3:
        raise HTTPException(
            status_code=400,
            detail="Member cannot borrow more than 3 active books"
        )

    existing_borrow = db.query(Borrow).filter(
        Borrow.book_id == borrow.book_id,
        Borrow.member_id == borrow.member_id,
        Borrow.status.in_(["Borrowed", "Overdue"])
    ).first()

    if existing_borrow:
        raise HTTPException(
            status_code=400,
            detail="Member has already borrowed this book"
        )

    borrow_date = date.today()
    due_date = borrow_date + timedelta(days=14)

    new_borrow = Borrow(
        book_id=borrow.book_id,
        member_id=borrow.member_id,
        borrow_date=borrow_date,
        due_date=due_date,
        status="Borrowed"
    )

    book.available_copies -= 1

    db.add(new_borrow)
    db.commit()
    db.refresh(new_borrow)

    return new_borrow

@router.put("/return/{borrow_id}", response_model=BorrowResponse)
def return_book(
    borrow_id: int,
    db: Session = Depends(get_db)
):
    borrow = db.query(Borrow).filter(
        Borrow.id == borrow_id
    ).first()

    if not borrow:
        raise HTTPException(
            status_code=404,
            detail="Borrow record not found"
        )

    if borrow.status == "Returned":
        raise HTTPException(
            status_code=400,
            detail="Book has already been returned"
        )

    book = db.query(Book).filter(
        Book.id == borrow.book_id
    ).first()

    borrow.return_date = date.today()
    borrow.status = "Returned"

    if book.available_copies < book.total_copies:
        book.available_copies += 1

    db.commit()
    db.refresh(borrow)

    return borrow

@router.get("/members/{member_id}/books", response_model=list[BorrowResponse])
def get_member_books(
    member_id: int,
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )

    borrows = db.query(Borrow).filter(
        Borrow.member_id == member_id,
        Borrow.status.in_(["Borrowed", "Overdue"])
    ).all()

    return borrows

@router.get("/overdue", response_model=list[BorrowResponse])
def get_overdue_books(
    db: Session = Depends(get_db)
):
    today = date.today()

    overdue_borrows = db.query(Borrow).filter(
        Borrow.due_date < today,
        Borrow.status == "Borrowed"
    ).all()

    for borrow in overdue_borrows:
        borrow.status = "Overdue"

    db.commit()

    return overdue_borrows

@router.get("/books/{book_id}/borrow-history", response_model=list[BorrowResponse])
def get_book_borrow_history(
    book_id: int,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    borrows = db.query(Borrow).filter(
        Borrow.book_id == book_id
    ).all()

    return borrows