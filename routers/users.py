from fastapi import APIRouter, Depends
from fastapi import HTTPException
from core.crud import authenticate_user
from sqlalchemy.orm import Session
from core import crud, schemas, database


router = APIRouter()
get_db = database.get_db


#login validation
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login API endpoint
    - Accepts JSON with username and password
    - Validates credentials from database
    - Returns 200 OK if valid, 401 Unauthorized if invalid
    """
    db_user = crud.authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": f"Welcome {db_user.username}!"}


# Create Users
@router.post("/",response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate, db:Session= Depends(get_db)):
    return crud.create_user(db,user)

# Get user by ID
@router.get("/{user_id}",response_model=schemas.UserOut)
def read_user(user_id:int, db : Session=Depends(get_db)):
    return crud.get_user(db,user_id)

# Update user
@router.put("/{user_id}",response_model=schemas.UserOut)
def update_user(user_id:int,user:schemas.UserUpdate, db: Session=Depends(get_db)):
    return crud.update_user(db,user_id,user)

# Delete user
@router.delete("/{user_id}",response_model=schemas.UserOut)
def delete_user(user_id:int,db:Session=Depends(get_db)):
    return crud.delete_user(db,user_id)
"""
# User login
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": f"Welcome {db_user.username}!"}
"""

