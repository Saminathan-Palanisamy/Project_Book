from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime
from sqlalchemy import DateTime

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    bio = Column(Text)

    books = relationship("Book", back_populates="author", cascade="all, delete")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="SET NULL"))
    description = Column(Text)

    author = relationship("Author", back_populates="books")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True,index= True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed passwords

#---------------- Purchase ----------------
class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    quantity = Column(Integer, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    book = relationship("Book")
