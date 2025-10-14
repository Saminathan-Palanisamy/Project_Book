from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core import models, schemas, database
from core.auth import get_current_user
#same admin/approved-vendor rule

router = APIRouter()
get_db = database.get_db

def require_admin_or_approved_vendor(current_user: models.User):
    if current_user.role == models.UserRole.ADMIN:
        return current_user
    if current_user.role == models.UserRole.VENDOR:
        if getattr(current_user, "vendor_profile", None) and current_user.vendor_profile.verified == "approved":
            return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized, anumadhi ilama suma suma nonda kudadhu")


@router.post("/", response_model=schemas.BookOut, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin_or_approved_vendor(current_user)
    try:
        # optional: verify author exists if author_id provided
        if book.author_id:
            author = db.query(models.Author).filter(models.Author.id == book.author_id).first()
            if not author:
                raise HTTPException(status_code=404, detail="Author not found, ungaluku anumadhu ilai")
        db_book = models.Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

@router.get("/{book_id}", response_model=schemas.BookOut)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found, book kanama pochu")
    return book

@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin_or_approved_vendor(current_user)
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found, library laye ilayam")
    for key, value in book.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin_or_approved_vendor(current_user)
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found, irukura book ah thedungo")
    db.delete(db_book)
    db.commit()
    return {"detail": "Book deleted successfully"}
