from fastapi import FastAPI

from app.database import Base, engine
from app.models.category import Category
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from app.routers.category import router as category_router
from app.routers.book import router as book_router
from app.routers.member import router as member_router
from app.routers.borrow import router as borrow_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System")
app.include_router(category_router)
app.include_router(book_router)
app.include_router(member_router)
app.include_router(borrow_router)


@app.get("/")
def home():
    return {"message": "Library Management System is running"}