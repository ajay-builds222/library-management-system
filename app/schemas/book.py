from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    category_id: int
    total_copies: int
    available_copies: int
    published_year: int | None = None


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)