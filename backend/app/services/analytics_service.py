from typing import Any

from app.algorithms.top_k import TopKHeap
from app.db.models.order import OrderItem
from app.db.models.product import Product
from sqlalchemy import func
from sqlalchemy.orm import Session


class AnalyticsService:
    def get_top_k_products(self, db: Session, k: int = 10) -> list[dict[str, Any]]:
        # Query total quantity sold per product across non-failed orders
        results = (
            db.query(
                Product.id,
                Product.sku,
                Product.name,
                Product.brand,
                Product.price,
                func.coalesce(func.sum(OrderItem.quantity), 0).label("sales_count")
            )
            .outerjoin(OrderItem, Product.id == OrderItem.product_id)
            .group_by(Product.id)
            .all()
        )

        items = [
            {
                "id": r.id,
                "sku": r.sku,
                "name": r.name,
                "brand": r.brand,
                "price": float(r.price),
                "sales_count": int(r.sales_count)
            }
            for r in results
        ]

        # Use Top-K Heap algorithm (O(N log K) time complexity)
        return TopKHeap.get_top_k_products(items, k=k, metric_key="sales_count")

analytics_service = AnalyticsService()
