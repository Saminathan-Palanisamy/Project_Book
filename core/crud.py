from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core import models, schemas
from fastapi import HTTPException

# ---------------- Authors ----------------
def create_author(db: Session, author: schemas.AuthorCreate):
    try:
        db_author = models.Author(**author.dict())
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
        return db_author
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def get_author(db: Session, author_id: int):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

def update_author(db: Session, author_id: int, author_data: schemas.AuthorUpdate):
    author = get_author(db, author_id)
    try:
        for key, value in author_data.dict(exclude_unset=True).items():
            setattr(author, key, value)
        db.commit()
        db.refresh(author)
        return author
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_author(db: Session, author_id: int):
    author = get_author(db, author_id)
    try:
        db.delete(author)
        db.commit()
        return {"detail": "Author deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- Books ----------------
def create_book(db: Session, book: schemas.BookCreate):
    try:
        db_book = models.Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def get_book(db: Session, book_id: int):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

def update_book(db: Session, book_id: int, book_data: schemas.BookUpdate):
    book = get_book(db, book_id)
    try:
        for key, value in book_data.dict(exclude_unset=True).items():
            setattr(book, key, value)
        db.commit()
        db.refresh(book)
        return book
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_book(db: Session, book_id: int):
    book = get_book(db, book_id)
    try:
        db.delete(book)
        db.commit()
        return {"detail": "Book deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- Users ----------------
def create_user(db: Session, user: schemas.UserCreate):
    try:
        db_user = models.User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate):
    user = get_user(db, user_id)
    try:
        for key, value in user_data.dict(exclude_unset=True).items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    try:
        db.delete(user)
        db.commit()
        return {"detail": "User deleted"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
"""
#------login verification-----------------
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username,
                                        models.User.password == password).first()
    return user  # returns None if invalid
"""
def authenticate_user(db: Session, username: str, password: str):
    """
    Checks if a user exists with the given username and password.
    Returns the User object if valid, else None.
    """
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.password == password
    ).first()
    return user
