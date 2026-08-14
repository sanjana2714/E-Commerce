from app.db.repositories.user_repository import user_repository, UserRepository
from app.db.repositories.product_repository import product_repository, ProductRepository
from app.db.repositories.order_repository import order_repository, OrderRepository
from app.db.repositories.inventory_repository import inventory_repository, InventoryRepository
from app.db.repositories.outbox_repository import outbox_repository, OutboxRepository

__all__ = [
    "user_repository",
    "UserRepository",
    "product_repository",
    "ProductRepository",
    "order_repository",
    "OrderRepository",
    "inventory_repository",
    "InventoryRepository",
    "outbox_repository",
    "OutboxRepository",
]
