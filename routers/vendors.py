from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.models import User, VendorProfile, Book, Purchase
from core.schemas import BookOut, PurchaseOut  # <-- use PurchaseOut instead of SaleOut
from core.auth import get_current_user

router = APIRouter()

# Dependency
def require_approved_vendor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == current_user.id).first()
    
    if not vendor_profile:
        raise HTTPException(status_code=403, detail="Vendor profile not found")
    
    # normalize string to avoid case/space issues
    if vendor_profile.verified.strip().lower() != "approved":
        raise HTTPException(status_code=403, detail="Vendor not approved")
    
    return current_user

# Dashboard
@router.get("/dashboard")
def vendor_dashboard(current_user: User = Depends(require_approved_vendor), db: Session = Depends(get_db)):
    vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == current_user.id).first()
    books_count = db.query(Book).filter(Book.author_id == current_user.id).count()
    authors_count = db.query(User).filter(User.role == "vendor").count()
    purchases_count = db.query(Purchase).join(Book).filter(Book.author_id == current_user.id).count()
    return {
        "username": current_user.username,
        "business_name": vendor_profile.business_name,
        "books_count": books_count,
        "authors_count": authors_count,
        "purchases_count": purchases_count
    }

# Vendor books
@router.get("/books", response_model=List[BookOut])
def vendor_books(current_user: User = Depends(require_approved_vendor), db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.author_id == current_user.id).all()
    return books

# Vendor sales
@router.get("/sales", response_model=List[PurchaseOut])  # <-- corrected
def vendor_sales(current_user: User = Depends(require_approved_vendor), db: Session = Depends(get_db)):
    sales = db.query(Purchase).join(Book).filter(Book.author_id == current_user.id).all()
    return sales
