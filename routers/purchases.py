# routers/purchases.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List

from core import models, schemas, database
from core.auth import get_current_user

router = APIRouter()
get_db = database.get_db

@router.post("/", response_model=schemas.PurchaseResponse, status_code=201)
def buy_book(
    purchase: schemas.PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a purchase for a book.
    Only the logged-in user can purchase for themselves unless admin.
    """
    # Non-admin cannot purchase for others
    if current_user.role != models.UserRole.ADMIN and hasattr(purchase, "user_id"):
        raise HTTPException(status_code=403, detail="Not authorized to create purchase for another user")

    book = db.query(models.Book).filter(models.Book.id == purchase.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
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

# ---------------------------------------------------------------------
# 🧾 Vendor Sales Report: All purchases for books uploaded by a vendor
@router.get("/vendor/{vendor_id}", response_model=List[schemas.PurchaseResponse])
def get_vendor_sales(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Only the vendor themselves or admin can see
    if current_user.role != models.UserRole.ADMIN and current_user.id != vendor_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these sales")

    # Get all books created by this vendor
    books = db.query(models.Book).filter(models.Book.vendor_id == vendor_id).all()
    book_ids = [b.id for b in books]

    if not book_ids:
        return []

    # Get all purchases for these books
    purchases = db.query(models.Purchase).filter(models.Purchase.book_id.in_(book_ids)).all()
    return purchases
