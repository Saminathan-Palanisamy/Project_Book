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
    model_config = {
        "from_attributes": True
    }

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
    model_config = {
        "from_attributes": True
    }

# ---------------- Users ----------------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    

class UserCreate(BaseModel):
    username: str
    email: EmailStr 
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    username: str
    email: EmailStr
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
    model_config = {
        "from_attributes": True
    }

#---------------- Auth[JWT] ----------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None