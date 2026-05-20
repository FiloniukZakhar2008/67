from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud import profile, user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import ProfileCreate, ProfileRead, ProfileUpdate, UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.get("/profiles/", response_model=list[ProfileRead])
async def read_profiles(db: AsyncSession = Depends(get_db)):
    return await profile.get_multi(db)


@router.post("/profiles/", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(obj_in: ProfileCreate, db: AsyncSession = Depends(get_db)):
    return await profile.create(db, obj_in)


@router.patch("/profiles/{profile_id}", response_model=ProfileRead)
async def update_profile(profile_id: int, obj_in: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    db_profile = await profile.get(db, profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return await profile.update(db, db_profile, obj_in)


@router.get("/", response_model=list[UserRead])
async def read_users(db: AsyncSession = Depends(get_db)):
    return await user.get_multi(db)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(obj_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user.get_by_email(db, obj_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    return await user.create(db, obj_in)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_current_user(
    obj_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if obj_in.email and obj_in.email != current_user.email:
        existing_user = await user.get_by_email(db, obj_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    return await user.update(db, current_user, obj_in)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await user.get(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, obj_in: UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await user.get(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await user.update(db, db_user, obj_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await user.remove(db, user_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="User not found")