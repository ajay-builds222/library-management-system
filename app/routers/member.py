from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.member import Member
from app.schemas.member import MemberCreate, MemberResponse

router = APIRouter(
    prefix="/members",
    tags=["Members"]
)


@router.post("/", response_model=MemberResponse, status_code=201)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):

    existing = db.query(Member).filter(
        Member.email == member.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    new_member = Member(
        name=member.name,
        email=member.email,
        phone=member.phone,
        address=member.address,
        membership_date=member.membership_date,
        is_active=member.is_active
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member


@router.get("/", response_model=list[MemberResponse])
def get_members(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    members = db.query(Member).offset(skip).limit(limit).all()

    return members


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
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

    return member


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    member: MemberCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )

    duplicate = db.query(Member).filter(
        Member.email == member.email,
        Member.id != member_id
    ).first()

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    existing.name = member.name
    existing.email = member.email
    existing.phone = member.phone
    existing.address = member.address
    existing.membership_date = member.membership_date
    existing.is_active = member.is_active

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{member_id}", status_code=200)
def delete_member(
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

    db.delete(member)
    db.commit()

    return {"message": "Member deleted successfully"}