from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
from sqlalchemy import DateTime
import enum

# ----------- Role Enum -----------
class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VENDOR = "vendor"

# ----------- Author -----------
class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    bio = Column(Text)
    books = relationship("Book", back_populates="author", cascade="all, delete")

# ----------- Book -----------
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="SET NULL"))
    description = Column(Text)
    author = relationship("Author", back_populates="books")

# ----------- User -----------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    # Relationships
    purchases = relationship("Purchase", back_populates="user", cascade="all, delete")
    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False, cascade="all, delete")

# ----------- VendorProfile -----------
class VendorProfile(Base):
    __tablename__ = "vendor_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    business_name = Column(String(255), nullable=False)
    verified = Column(String(10), default="pending")  # 'pending', 'approved', 'rejected'

    user = relationship("User", back_populates="vendor_profile")

# ----------- Purchase -----------
class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    quantity = Column(Integer, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="purchases")
    book = relationship("Book")
