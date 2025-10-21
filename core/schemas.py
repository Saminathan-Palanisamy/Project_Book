from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from core.models import UserRole
import enum

# Re-declare small enum type for Pydantic use (string)
class UserRoleStr(str, enum.Enum):
    admin = "admin"
    user = "user"
    vendor = "vendor"

# ---------------- Authors ----------------
class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None

class AuthorCreate(AuthorBase): pass
class AuthorUpdate(AuthorBase): pass

class AuthorOut(AuthorBase):
    id: int
    model_config = {"from_attributes": True}

# ---------------- Books ----------------
class BookBase(BaseModel):
    title: str
    author_id: Optional[int] = None
    description: Optional[str] = None

class BookCreate(BookBase): pass
class BookUpdate(BookBase): pass

class BookOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: Optional[float]
    author_id: int

    class Config:
        orm_mode = True

# ---------------- Users ----------------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    #role: Optional[UserRole] = UserRole.USER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
   # role: Optional[UserRole] = None

class UserOut(UserBase):
    id: int
    role: Optional[UserRoleStr] = UserRoleStr.user
    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    username: str
    password: str

# ---------------- Purchases ----------------
class PurchaseBase(BaseModel):
    
    book_id: int
    quantity: int

class PurchaseCreate(PurchaseBase): pass

class PurchaseResponse(PurchaseBase):
    id: int
    user_id: int
    purchase_date: datetime
    model_config = {"from_attributes": True}

# ---------------- Vendor ----------------
class VendorCreate(BaseModel):
    business_name: str

class VendorOut(BaseModel):
    id: int
    user_id: int
    business_name: str
    verified: str
    model_config = {"from_attributes": True}

# ---------------- Auth[JWT] ----------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ---------------- Purchase Output ----------------

class PurchaseOut(BaseModel):
    id: int
    book_id: int
    user_id: int
    quantity: int
    total_amount: Optional[float] = 0

    class Config:
        orm_mode = True