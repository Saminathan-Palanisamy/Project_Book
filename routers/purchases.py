from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from core import models, schemas, database
from core.auth import get_current_user

router = APIRouter()
get_db = database.get_db

@router.post("/", response_model=schemas.PurchaseResponse, status_code=201)
def buy_book(purchase: schemas.PurchaseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # do not trust client-provided user_id; use current_user.id
    if purchase.user_id != current_user.id and current_user.role != models.UserRole.ADMIN:
        # non-admin cannot purchase on behalf of others
        raise HTTPException(status_code=403, detail="Not authorized to create purchase for another user")

    book = db.query(models.Book).filter(models.Book.id == purchase.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
        db_purchase = models.Purchase(
            user_id=current_user.id if current_user.role != models.UserRole.ADMIN else purchase.user_id,
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