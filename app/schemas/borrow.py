from datetime import date
from pydantic import BaseModel, ConfigDict


class BorrowCreate(BaseModel):
    book_id: int
    member_id: int


class BorrowResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrow_date: date
    due_date: date
    return_date: date | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)