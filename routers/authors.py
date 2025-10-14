from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core import models, schemas, database
from core.auth import get_current_user

router = APIRouter()
get_db = database.get_db
#enforce only ADMIN or approved VENDOR to mutate
def require_admin_or_approved_vendor(current_user: models.User):
    # admin allowed
    if current_user.role == models.UserRole.ADMIN:
        return current_user
    # vendor allowed only if vendor_profile exists and is approved
    if current_user.role == models.UserRole.VENDOR:
        if getattr(current_user, "vendor_profile", None) and current_user.vendor_profile.verified == "approved":
            return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.post("/", response_model=schemas.AuthorOut, status_code=201)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin_or_approved_vendor(current_user)
    try:
        db_author = models.Author(**author.dict())
        db.add(db_author)
        db.commit()
        db.refresh(db_author)
        return db_author
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

@router.get("/{author_id}", response_model=schemas.AuthorOut)
def read_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@router.put("/{author_id}", response_model=schemas.AuthorOut)
def update_author(author_id: int, author: schemas.AuthorUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin_or_approved_vendor(current_user)
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    for key, value in author.dict(exclude_unset=True).items():
        setattr(db_author, key, value)
    db.commit()
    db.refresh(db_author)
    return db_author

@router.delete("/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_admin_or_approved_vendor(current_user)
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(db_author)
    db.commit()
    return {"detail": "Author deleted successfully"}
