import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.models import User, UserRole, Category, Product, ProductStatus, Inventory
from app.core.security import hash_password, create_access_token

# Use SQLite in-memory for fast isolated unit/integration tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_headers(db_session):
    user = User(
        email="admin_test@example.com",
        full_name="Test Admin",
        hashed_password=hash_password("password"),
        role=UserRole.ADMIN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def customer_headers(db_session):
    user = User(
        email="customer_test@example.com",
        full_name="Test Customer",
        hashed_password=hash_password("password"),
        role=UserRole.CUSTOMER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}
