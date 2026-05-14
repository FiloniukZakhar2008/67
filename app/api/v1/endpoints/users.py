from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import crud_user  # припускаємо, що тут твій CRUD
from app.schemas.user import UserResponse, UserCreate

router = APIRouter()

@router.get("/", response_model=list[UserResponse])
async def read_users(db: AsyncSession = Depends(get_db)):
    users = await crud_user.get_multi(db)
    return users

@router.post("/", response_model=UserResponse)
async def create_user(obj_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud_user.create(db, obj_in=obj_in)

@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "id": current_user.id}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}