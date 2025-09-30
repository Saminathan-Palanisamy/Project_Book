from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core import crud, schemas, database

router = APIRouter()
get_db = database.get_db

# Create a book
@router.post("/", response_model=schemas.BookOut)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, book)

# Get book by ID
@router.get("/{book_id}", response_model=schemas.BookOut)
def read_book(book_id: int, db: Session = Depends(get_db)):
    return crud.get_book(db, book_id)

# Update book
@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int,book: schemas.BookUpdate, db: Session = Depends(get_db)):
    return crud.update_book(db, book_id, book)

# Delete book
@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return crud.delete_book(db, book_id)
