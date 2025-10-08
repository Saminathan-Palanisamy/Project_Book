from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from core import models, schemas, database
from core.auth import get_current_user

router = APIRouter()
get_db = database.get_db

@router.post("/", response_model=schemas.PurchaseResponse)
def buy_book(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        # Use current_user.id instead of trusting client-sent user_id
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        book = db.query(models.Book).filter(models.Book.id == purchase.book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        db_purchase = models.Purchase(
            user_id=current_user.id,
            book_id=purchase.book_id,
            quantity=purchase.quantity,
            purchase_date=datetime.utcnow()
        )

        db.add(db_purchase)
        db.commit()
        db.refresh(db_purchase)
        return db_purchase

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
