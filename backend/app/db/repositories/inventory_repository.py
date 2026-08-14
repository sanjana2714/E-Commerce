
from app.db.models.inventory import Inventory
from sqlalchemy.orm import Session


class InventoryRepository:
    def get_by_product_id(self, db: Session, product_id: int, lock: bool = False) -> Inventory | None:
        query = db.query(Inventory).filter(Inventory.product_id == product_id)
        if lock and db.bind and db.bind.dialect.name != "sqlite":
            query = query.with_for_update()
        return query.first()

    def update_stock(self, db: Session, inventory: Inventory, stock_delta: int, reserved_delta: int) -> Inventory:
        inventory.stock_quantity += stock_delta
        inventory.reserved_quantity = max(0, inventory.reserved_quantity + reserved_delta)
        inventory.version += 1
        db.flush()
        return inventory

inventory_repository = InventoryRepository()
