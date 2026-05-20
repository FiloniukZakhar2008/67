import os
import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.models  # noqa: F401 - реєструємо всі моделі в Base.metadata
from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://user:pass@localhost:5434/test_db",
)


# 1. Глобальний event loop для стабільності pytest-asyncio
@pytest.fixture(scope="session", autouse=True)
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# 2. Фікстура для створення Engine на кожен тест.
# Це вирішує проблему InterfaceError (пул завжди свіжий)
@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Перед тестом створюємо таблиці (якщо їх немає)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Після тесту дропаємо, щоб наступний тест починав з чистого листа
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# 3. Створення фабрики сесій для конкретного тесту
@pytest_asyncio.fixture(scope="function")
async def session_factory(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False)


# 4. Чиста сесія бази даних для CRUD тестів
@pytest_asyncio.fixture(scope="function")
async def db_session(session_factory):
    async with session_factory() as session:
        yield session
        await session.rollback()


# 5. Клієнт для API тестів з правильним перевизначенням залежностей
@pytest_asyncio.fixture(scope="function")
async def client(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    # Підміняємо депенденсі у FastAPI
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
    ) as test_client:
        yield test_client

    # Очищаємо після завершення тесту
    app.dependency_overrides.clear()