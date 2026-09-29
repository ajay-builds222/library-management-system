# Library Management System

A backend application for managing a library using FastAPI, SQLAlchemy, and MySQL.

## Technologies Used

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- MySQL
- PyMySQL
- Uvicorn

## Features

### Categories
- Create category
- View categories
- Get category by ID
- Update category
- Delete category

### Books
- Add books
- View books
- Get book by ID
- Update books
- Delete books
- Search books by title, author, or category
- Pagination

### Members
- Add members
- View members
- Get member by ID
- Update members
- Delete members
- Email and phone validation
- Pagination

### Borrow and Return
- Borrow books
- Return books
- Track borrowed books
- View member borrowing history
- View book borrowing history
- Detect overdue books
- Maximum 3 active books per member
- Prevent borrowing unavailable books
- Prevent inactive members from borrowing

## Assumptions

- MySQL is installed and running before starting the application.
- The MySQL database `LibraryBackendDB` is created before running the application.
- Database credentials are stored in the `.env` file.
- The `.env` file is not committed to GitHub for security reasons.
- A member can have a maximum of 3 active borrowed books.
- A book cannot be borrowed when its available copies are 0.
- A member must be active to borrow a book.
- A member cannot borrow the same book again until the previous borrow is returned.
- The due date is automatically set to 14 days from the borrow date.
- Books with an active `Borrowed` or `Overdue` record cannot be deleted.
- Search by title and author uses partial matching.
- Pagination uses `skip` and `limit` query parameters.
- Overdue status is assigned to borrowed books whose due date has passed.

## Project Structure

```text
app/
├── main.py
├── database.py
├── models/
├── schemas/
├── routers/
└── services/

.env
.gitignore
requirements.txt
README.md