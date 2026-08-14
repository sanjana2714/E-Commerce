import os
import time
import uuid
import concurrent.futures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import User, UserRole, Category, Product, ProductStatus, Inventory
from app.services.order_service import order_service
from app.schemas.order import OrderCreate, OrderCreateItem
from app.core.exceptions import InsufficientInventoryError

def get_test_engine():
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if test_db_url and test_db_url.startswith("postgresql"):
        # Real Postgres engine to support high concurrency testing
        return create_engine(test_db_url, pool_size=50, max_overflow=50)

    db_file = "./test_concurrency_isolated.db"
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass
    return create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False, "timeout": 30.0})

def test_concurrent_inventory_reservations():
    """
    Simulates 100 concurrent purchase requests against a product with stock = 10.
    Verifies row-level locking (SELECT FOR UPDATE) / transaction boundary guarantees:
    1. Exactly 10 reservations succeed.
    2. 90 reservations fail with InsufficientInventoryError.
    3. Final stock_quantity is strictly 0.
    4. Stock NEVER goes negative.
    """
    engine = get_test_engine()
    is_postgres = "postgresql" in str(engine.url)
    if is_postgres:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    # Setup isolated product & inventory
    setup_db = Session()
    sku = f"CONCUR-TEST-{uuid.uuid4().hex[:6]}"
    cat = Category(name="Concurrency Cat", slug=f"concur-cat-{uuid.uuid4().hex[:4]}")
    setup_db.add(cat)
    setup_db.commit()

    user = User(email=f"concur_user_{uuid.uuid4().hex[:6]}@example.com", full_name="Concur User", hashed_password="pwd", role=UserRole.CUSTOMER)
    setup_db.add(user)
    setup_db.commit()

    product = Product(
        sku=sku,
        name="Flash Sale Phone",
        category_id=cat.id,
        brand="SpeedTech",
        price=500.0,
        status=ProductStatus.ACTIVE
    )
    setup_db.add(product)
    setup_db.flush()

    inventory = Inventory(
        product_id=product.id,
        stock_quantity=10,
        reserved_quantity=0,
        version=1
    )
    setup_db.add(inventory)
    setup_db.commit()
    product_id = product.id
    user_id = user.id
    setup_db.close()

    def attempt_purchase(idx: int):
        max_retries = 20
        for attempt in range(max_retries):
            db = Session()
            try:
                order_in = OrderCreate(items=[OrderCreateItem(product_id=product_id, quantity=1)])
                key = f"CONCUR-KEY-{idx}-{uuid.uuid4()}"
                order = order_service.create_order_idempotent(db, user_id=user_id, idempotency_key=key, order_in=order_in)
                return ("SUCCESS", order.id)
            except InsufficientInventoryError:
                return ("INSUFFICIENT_STOCK", None)
            except Exception as e:
                db.rollback()
                err_str = str(e)
                if "locked" in err_str.lower() or "busy" in err_str.lower():
                    time.sleep(0.02 * (attempt + 1))
                    continue
                return ("ERROR", err_str)
            finally:
                db.close()
        return ("LOCKED_EXHAUSTED", None)

    # Launch 100 threads simultaneously
    results = []
    max_workers = 50 if is_postgres else 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(attempt_purchase, i) for i in range(100)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    successes = [r for r in results if r[0] == "SUCCESS"]
    out_of_stock = [r for r in results if r[0] == "INSUFFICIENT_STOCK"]

    # Verify results against strict invariants
    verify_db = Session()
    final_inv = verify_db.query(Inventory).filter(Inventory.product_id == product_id).first()

    assert len(successes) == 10, f"Expected exactly 10 successes, got {len(successes)}"
    assert len(out_of_stock) == 90, f"Expected 90 stock failures, got {len(out_of_stock)}"
    assert final_inv is not None, "Final inventory record not found!"
    assert final_inv.stock_quantity == 0, f"Expected final stock 0, got {final_inv.stock_quantity}"
    assert final_inv.stock_quantity >= 0, "Inventory went negative!"
    assert final_inv.reserved_quantity == 10, f"Expected 10 reserved, got {final_inv.reserved_quantity}"

    verify_db.close()
    print("\nConcurrency Test Passed: Zero overselling, zero negative inventory, exact row locking verified!")

if __name__ == "__main__":
    test_concurrent_inventory_reservations()
