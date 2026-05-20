from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.crud import user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def set_access_token_cookie(response: Response, user_id: int) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": str(user_id)}, expires_delta=expires_delta)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=int(expires_delta.total_seconds()),
        samesite="lax",
    )
    return token


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(response: Response, obj_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user.get_by_email(db, obj_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    db_user = await user.create(db, obj_in)
    set_access_token_cookie(response, db_user.id)
    return db_user


@router.post("/login")
async def login(response: Response, credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    db_user = await user.get_by_email(db, credentials.email)
    if db_user is None or not verify_password(credentials.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    set_access_token_cookie(response, db_user.id)
    return {"message": "Logged in successfully"}


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
