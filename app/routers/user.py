
from fastapi import Depends, HTTPException,APIRouter
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..schemas import UserCreate,UserOut  
from fastapi import status
from ..utils import hash

router = APIRouter(prefix="/users",tags=["Users"])

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user.password=hash(user.password)
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return  new_user

@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        return user
    return {"message": "User not found"}, status.HTTP_404_NOT_FOUND