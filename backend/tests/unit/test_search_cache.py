import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Product, Category, ProductStatus
from app.services.search_service import search_service

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    cat = Category(name="Electronics", slug="electronics")
    session.add(cat)
    session.commit()

    p1 = Product(sku="PROD-001", name="Wireless Mouse", brand="LogiTech", category_id=cat.id, price=29.99, status=ProductStatus.ACTIVE)
    p2 = Product(sku="PROD-002", name="Gaming Keyboard", brand="Razer", category_id=cat.id, price=89.99, status=ProductStatus.ACTIVE)
    session.add_all([p1, p2])
    session.commit()

    yield session
    session.close()

@pytest.mark.asyncio
async def test_sql_fallback_search(db_session):
    # Ensure fallback database search works when OpenSearch client is not connected
    from app.search.opensearch_client import opensearch_manager
    opensearch_manager.client = None

    search_res = await search_service.search_products(db=db_session, query="Mouse")
    assert search_res["total"] == 1
    assert search_res["hits"][0]["name"] == "Wireless Mouse"

@pytest.mark.asyncio
async def test_search_all_products(db_session):
    from app.search.opensearch_client import opensearch_manager
    opensearch_manager.client = None

    search_res = await search_service.search_products(db=db_session, query="")
    assert search_res["total"] == 2
