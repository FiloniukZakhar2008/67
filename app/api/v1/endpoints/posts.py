from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import post
from app.db.session import get_db
from app.schemas.post import PostCreate, PostRead, PostUpdate

router = APIRouter()


@router.get("/", response_model=list[PostRead])
async def read_posts(db: AsyncSession = Depends(get_db)):
    return await post.get_multi(db)


@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(obj_in: PostCreate, db: AsyncSession = Depends(get_db)):
    return await post.create(db, obj_in)


@router.get("/{post_id}", response_model=PostRead)
async def read_post(post_id: int, db: AsyncSession = Depends(get_db)):
    db_post = await post.get(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(post_id: int, obj_in: PostUpdate, db: AsyncSession = Depends(get_db)):
    db_post = await post.get(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return await post.update(db, db_post, obj_in)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await post.remove(db, post_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Post not found")