from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class MemberBase(BaseModel):
    name: str
    email: EmailStr
    phone: str = Field(
        min_length=10,
        max_length=10,
        pattern=r"^[0-9]{10}$"
    )
    address: str | None = None
    membership_date: date
    is_active: bool = True


class MemberCreate(MemberBase):
    pass


class MemberResponse(MemberBase):
    id: int

    model_config = ConfigDict(from_attributes=True)