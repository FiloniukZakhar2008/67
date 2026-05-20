from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.crud import user
from app.db.session import get_db
from app.models.user import User

async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


async def get_current_user(
        access_token: str | None = Cookie(default=None),
        db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    if access_token is None:
        raise credentials_exception

    payload = decode_access_token(access_token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception

    current_user = await user.get(db, user_id_int)
    if current_user is None:
        raise credentials_exception
    return current_user