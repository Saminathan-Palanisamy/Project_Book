from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core import crud, schemas, database

router = APIRouter()
get_db = database.get_db

# Create Users
@router.post("/",response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate, db:Session= Depends(get_db)):
    return crud.create_user(db,user)

# Get user by ID
@router.get("{/user_id}",response_model=schemas.UserOut)
def read_user(user_id:int, db : Session=Depends(get_db)):
    return crud.get_user(db,user_id)

# Update user
@router.put("{/user_id}",response_model=schemas.UserOut)
def update_user(user_id:int,user:schemas.UserUpdate, db: Session=Depends(get_db)):
    return crud.update_user(db,user_id,user)

# Delete user
def delete_user(user_id:int,db:Session=Depends(get_db)):
    return crud.delete_user(db,user_id)