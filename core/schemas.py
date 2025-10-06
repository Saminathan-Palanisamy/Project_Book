from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ---------------- Authors ----------------
class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(AuthorBase):
    pass

class AuthorOut(AuthorBase):
    id: int
    class Config:
        orm_mode = True

# ---------------- Books ----------------
class BookBase(BaseModel):
    title: str
    author_id: Optional[int] = None
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class BookOut(BookBase):
    id: int
    class Config:
        orm_mode = True

# ---------------- Users ----------------
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    class Config:
        orm_mode = True

# ---------------- Users ----------------
class UserLogin(BaseModel):
    username: str
    password: str

# ---------------- Purchases ----------------
class PurchaseBase(BaseModel):
    user_id: int
    book_id: int
    quantity: int

class PurchaseError(Exception):
    pass
class PurchaseCreate(PurchaseBase):
    pass
class PurchaseResponse(PurchaseBase):
    id: int
    purchase_date: datetime
    class Config:
        orm_mode = True