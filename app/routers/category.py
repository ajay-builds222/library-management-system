from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(
        Category.category_name == category.category_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    new_category = Category(
        category_name=category.category_name,
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@router.get("/", response_model=list[CategoryResponse])
def get_categories(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Category).filter(Category.id == category_id).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    duplicate = db.query(Category).filter(
        Category.category_name == category.category_name,
        Category.id != category_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Category name already exists"
        )

    existing.category_name = category.category_name
    existing.description = category.description

    db.commit()
    db.refresh(existing)

    return existing

@router.delete("/{category_id}", status_code=200)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    if category.books:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category because books exist in this category"
        )

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}