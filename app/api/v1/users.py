from fastapi import APIRouter, HTTPException

from app.schemas.user import UserCreate, UserUpdate
from app.crud.crud_user import (
    get_users,
    get_user,
    create_user,
    update_user,
    delete_user
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/")
def read_users():
    return get_users()


@router.get("/{user_id}")
def read_user(user_id: int):
    user = get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.post("/")
def create_new_user(user: UserCreate):
    user_id = len(get_users()) + 1

    new_user = create_user(
        user_id,
        user.dict()
    )

    return {
        "id": user_id,
        **new_user
    }


@router.put("/{user_id}")
def update_existing_user(
    user_id: int,
    user: UserUpdate
):
    updated_user = update_user(
        user_id,
        user.dict(exclude_unset=True)
    )

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return updated_user


@router.delete("/{user_id}")
def delete_existing_user(user_id: int):
    deleted_user = delete_user(user_id)

    if not deleted_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully"
    }