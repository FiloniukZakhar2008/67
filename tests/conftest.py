import pytest
from sqlalchemy import create_mock_engine, create_engine
from sqlalchemy.orm import sessionmaker
from main import app  # імпорт вашого FastAPI додатку
from database import Base, get_db

# URL вашої тестової бази
TEST_SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost:5432/test_db"

engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Створюємо таблиці перед початком тестів та видаляємо після."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Фікстура для очищення таблиць після кожного тесту."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Підміна залежності get_db у FastAPI."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    yield TestClient(app)
    del app.dependency_overrides[get_db]