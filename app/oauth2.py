import jwt
from jwt import PyJWTError
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .schemas import TokenData
from datetime import timezone


SECERET_KEY="2c17e445f30628345a0c38a2bee511506576cd7f4585a76e8b9406e80b498f76"
ALGORITHM="HS256"
EXPIRATION_TIME_MINUTES=30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECERET_KEY,algorithm=ALGORITHM)
    return encoded_jwt
def verify_access_token(token:str,credentials_exception):
    try:
        payload=jwt.decode(token,SECERET_KEY,algorithms=[ALGORITHM],options={"require_exp": False})
        id:str=payload.get("sub")
        if id is None:
            raise credentials_exception
        user=TokenData(id=id)
        return user
       
    except (InvalidTokenError, ExpiredSignatureError):
        raise credentials_exception
    
    
def get_current_user(token:str=Depends(oauth2_scheme)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate":"Bearer"})
    return verify_access_token(token,credentials_exception)