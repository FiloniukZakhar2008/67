from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.core.security import get_password_hash
from app.models.user import Profile, User
from app.schemas.user import ProfileCreate, ProfileUpdate, UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: UserCreate | dict) -> User:
        data = obj_in.model_dump() if isinstance(obj_in, UserCreate) else obj_in.copy()
        password = data.pop("password")
        data["hashed_password"] = get_password_hash(password)
        return await super().create(db, data)


user = CRUDUser(User)
profile = CRUDBase[Profile, ProfileCreate, ProfileUpdate](Profile)