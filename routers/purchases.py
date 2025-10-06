from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core import schemas, crud, database
from core.crud import PurchaseError

router = APIRouter()

@router.post("/purchase", response_model=schemas.PurchaseResponse)
def buy_book(purchase: schemas.PurchaseCreate, db: Session = Depends(database.get_db)):
    try:
        result = crud.create_purchase(db=db, purchase=purchase)
        if not result:
            raise HTTPException(status_code=404, detail="Purchase could not be completed")
        return result
    except PurchaseError as e:
        raise HTTPException(status_code=400, detail=f"Purchase error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    