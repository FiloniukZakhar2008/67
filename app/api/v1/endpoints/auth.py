from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core import security
from app.crud import crud_user
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Перевірка чи існує користувач
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Хешуємо пароль перед збереженням
    user_in.password = security.hash_password(user_in.password)
    return await crud_user.create(db, obj_in=user_in)


@router.post("/login")
async def login(response: Response, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_by_email(db, email=user_in.email)
    if not user or not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = security.create_access_token({"sub": str(user.id)})

    # Встановлюємо кукі
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=3600,
        samesite="lax"
    )
    return {"message": "Logged in successfully"}