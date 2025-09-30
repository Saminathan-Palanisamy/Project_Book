from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core import crud, schemas, database

router = APIRouter()
get_db = database.get_db

# Create author
@router.post("/", response_model=schemas.AuthorOut)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    return crud.create_author(db, author)

# Get author by ID
@router.get("/{author_id}", response_model=schemas.AuthorOut)
def read_author(author_id: int, db: Session = Depends(get_db)):
    return crud.get_author(db, author_id)

# Update author
@router.put("/{author_id}", response_model=schemas.AuthorOut)
def update_author(author_id: int, author: schemas.AuthorUpdate, db: Session = Depends(get_db)):
    return crud.update_author(db, author_id, author)

# Delete author
@router.delete("/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db)):
    return crud.delete_author(db, author_id)
