
from fastapi import Depends, HTTPException, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from ..schemas import CreatePost, Post  , PostOut
from fastapi import status
from ..oauth2 import get_current_user

from sqlalchemy import func

router = APIRouter(prefix="/posts",tags=["Posts"])

@router.get("/", response_model=List[PostOut])
def get_posts(db: Session = Depends(get_db), limit:int=10,skip:int=0, search:Optional[str]=""):
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return  posts

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=Post)
def create_post(post: CreatePost,db: Session = Depends(get_db), user: int = Depends(get_current_user)):
    print("Current User ID:", user)  # For debugging purposes
    new_post = models.Post(**post.model_dump(), owner_id=int(user.id))

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return  new_post

@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if post:
        return post
    return {"message": "Post not found"}, status.HTTP_404_NOT_FOUND

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post:
        if post.owner_id != int(user_id.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
        db.delete(post)
        db.commit()
        return {"message": "Deleted Successfully"}
    return {"message": "Post not found"}, status.HTTP_404_NOT_FOUND

@router.put("/{id}",status_code=status.HTTP_200_OK,response_model=Post)
def update_post(id: int, post: CreatePost, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    db.query(models.Post).filter(models.Post.id == id).update(post.model_dump(),synchronize_session=False)
    db.commit()
    updated_post = db.query(models.Post).filter(models.Post.id == id).first()
    if updated_post:
        if updated_post.owner_id != int(user_id.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
        return  updated_post
    return {"message": "Post not found"}, status.HTTP_404_NOT_FOUND
