from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta
import os
from core import models, schemas, database

from core.auth import (
    get_current_user,
    get_password_hash,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    require_admin,
    require_owner_or_admin
)


router = APIRouter()
get_db = database.get_db

# ---------------- Register ----------------
@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a normal user. role cannot be supplied by request (always USER).
    """
    try:
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if db.query(models.User).filter(models.User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            role=models.UserRole.USER  # enforce USER role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed: " + str(e))

# ---------------- Register as Vendor ----------------
@router.post("/register_vendor", response_model=schemas.VendorOut)
def register_vendor(
    vendor: schemas.VendorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.USER:
        raise HTTPException(status_code=400, detail="Only normal users can become vendors")

    db_vendor = models.VendorProfile(
        user_id=current_user.id,
        business_name=vendor.business_name,
        verified="pending"
    )
    db.add(db_vendor)
    current_user.role = models.UserRole.VENDOR
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

# ---------------- Create Admin (one-time, protected) ----------------
@router.post("/create_admin", response_model=schemas.UserOut, status_code=201)
def create_admin(
    user: schemas.UserCreate,
    admin_key: str,
    db: Session = Depends(get_db)
):
    """
    Create the ADMIN user. This endpoint should be protected by a secret key (ADMIN_CREATE_KEY)
    passed as admin_key param. It allows creating admin only if no admin exists.
    """
    ADMIN_CREATE_KEY = os.getenv("ADMIN_CREATE_KEY", None)
    if ADMIN_CREATE_KEY is None:
        raise HTTPException(status_code=500, detail="ADMIN_CREATE_KEY is not configured on server")

    if admin_key != ADMIN_CREATE_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin creation key")

    # check if admin already exists
    existing_admin = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin user already exists")

    try:
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if db.query(models.User).filter(models.User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            role=models.UserRole.ADMIN
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Admin creation failed: " + str(e))


# ---------------- Login ----------------
@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}






    #------let's add the current user details endpoint-----
@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Get details of the currently logged-in user.
    Token is required (Bearer token from login).
    """

    return current_user
#------------------------------------------------------
# ---------------- List all users (admin only) ----------------
@router.get("/all")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        if current_user.role != models.UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Permission denied")

        users = db.query(models.User).all()

        user_list = []
        for u in users:
            print("DEBUG User ->", u.id, u.username, u.role)  # 🧩 See what `u.role` actually is
            user_list.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": getattr(u.role, "value", u.role)
            })

        return user_list

    except Exception as e:
        import traceback
        traceback.print_exc()  # 🧩 This prints the full error trace
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    

# ---------------- Read User ----------------
@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # read permission: everyone can view details, but consider redacting sensitive fields in future
    return user

# ---------------- Admin approves vendor ----------------
@router.post("/approve_vendor/{vendor_profile_id}", response_model=schemas.VendorOut)
def approve_vendor(
    vendor_profile_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """
    Only ADMIN can approve or reject vendor.
    Approving sets VendorProfile.verified = 'approved' and promotes user.role -> VENDOR.
    """
    vp = db.query(models.VendorProfile).filter(models.VendorProfile.id == vendor_profile_id).first()
    if not vp:
        raise HTTPException(status_code=404, detail="Vendor profile not found")

    if vp.verified == "approved":
        raise HTTPException(status_code=400, detail="Vendor is already approved")

    try:
        vp.verified = "approved"
        # promote user to vendor
        user = db.query(models.User).filter(models.User.id == vp.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Associated user not found")
        user.role = models.UserRole.VENDOR
        db.commit()
        db.refresh(vp)
        return vp
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Vendor approval failed: " + str(e))


# ---------------- Admin rejects vendor ----------------
@router.post("/reject_vendor/{vendor_profile_id}", response_model=schemas.VendorOut)
def reject_vendor(
    vendor_profile_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    vp = db.query(models.VendorProfile).filter(models.VendorProfile.id == vendor_profile_id).first()
    if not vp:
        raise HTTPException(status_code=404, detail="Vendor profile not found")

    if vp.verified == "rejected":
        raise HTTPException(status_code=400, detail="Vendor is already rejected")

    try:
        vp.verified = "rejected"
        # keep user as USER (no role change) or revert if previously changed
        user = db.query(models.User).filter(models.User.id == vp.user_id).first()
        db.commit()
        db.refresh(vp)
        return vp
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Vendor rejection failed: " + str(e))
# ---------------- Get Vendor Profile by User ID ----------------
@router.get("/vendor_profile/{user_id}", response_model=schemas.VendorOut)
def get_vendor_profile(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Get the VendorProfile for a given user_id.
    Any logged-in user can view this, admin will use it for approvals.
    """
    vp = db.query(models.VendorProfile).filter(models.VendorProfile.user_id == user_id).first()
    if not vp:
        raise HTTPException(status_code=404, detail="Vendor profile not found")
    return vp

# ---------------- Update User ----------------
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):
    """
    Only admin or the owner can update user details. One user cannot update another user.
    role cannot be changed via this endpoint.
    """
    # check owner or admin
    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.dict(exclude_unset=True)
    # disallow role changes here
    if "role" in update_data:
        update_data.pop("role", None)

    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    try:
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Update failed: " + str(e))

# ---------------- Delete User ----------------
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Only admin OR the owner can delete a user. Users cannot delete other users.
    """
    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.delete(db_user)
        db.commit()
        return {"detail": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Delete failed: " + str(e))
    



