from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
# Імпортуй свої CRUD та Схеми

router = APIRouter()

@router.get("/")
async def get_products(db: AsyncSession = Depends(get_db)):
    # Логіка отримання товарів з БД
    pass