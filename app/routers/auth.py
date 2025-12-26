from fastapi import Depends, HTTPException, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from fastapi import status
from ..schemas import  UserLogin
from ..utils import  verify
from ..oauth2 import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas import Token

router = APIRouter(tags=["Auth"])

@router.post("/login",response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # user_credentials had username and password attributes
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user or not verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}