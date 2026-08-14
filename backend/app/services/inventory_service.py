from typing import Optional
import threading
from sqlalchemy.orm import Session
from app.db.models.inventory import Inventory
from app.core.exceptions import InsufficientInventoryError, ResourceNotFoundError
from app.core.logging import logger

_sqlite_lock = threading.Lock()

class InventoryService:
    def reserve_inventory_with_lock(self, db: Session, product_id: int, quantity: int) -> Inventory:
        """
        Locks the inventory row using SELECT ... FOR UPDATE within an active PostgreSQL transaction.
        In SQLite testing environments, uses an in-process thread lock fallback.
        Guarantees atomicity and prevents overselling under heavy concurrent load.
        """
        is_sqlite = db.get_bind().dialect.name == "sqlite" if db.bind or db.get_bind() else False

        if is_sqlite:
            _sqlite_lock.acquire()

        try:
            query = db.query(Inventory).filter(Inventory.product_id == product_id)
            if not is_sqlite:
                query = query.with_for_update()

            inventory = query.first()

            if not inventory:
                raise ResourceNotFoundError(f"Inventory record for product ID {product_id} not found.")

            if inventory.stock_quantity < quantity:
                logger.warning(
                    f"Concurrent reservation conflict for product {product_id}: "
                    f"Requested={quantity}, Available={inventory.stock_quantity}"
                )
                raise InsufficientInventoryError(
                    f"Cannot reserve {quantity} units for product ID {product_id}. "
                    f"Only {inventory.stock_quantity} available in stock."
                )

            # Deduct stock and update version count atomically
            inventory.stock_quantity -= quantity
            inventory.reserved_quantity += quantity
            inventory.version += 1

            if is_sqlite:
                db.commit()
            else:
                db.flush()

            return inventory
        finally:
            if is_sqlite:
                _sqlite_lock.release()

    def release_inventory(self, db: Session, product_id: int, quantity: int) -> Optional[Inventory]:
        """Releases reserved stock back to active stock_quantity upon order cancellation or payment failure."""
        inventory = (
            db.query(Inventory)
            .filter(Inventory.product_id == product_id)
            .with_for_update()
            .first()
        )
        if inventory:
            inventory.stock_quantity += quantity
            inventory.reserved_quantity = max(0, inventory.reserved_quantity - quantity)
            inventory.version += 1
            db.flush()
        return inventory

    def get_inventory(self, db: Session, product_id: int) -> Inventory:
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            raise ResourceNotFoundError(f"Inventory for product {product_id} not found.")
        return inventory

inventory_service = InventoryService()
