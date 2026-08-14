from typing import Any

from app.cache.redis_client import cache_service
from app.db.models.product import Product, ProductStatus
from app.search.opensearch_client import opensearch_manager
from sqlalchemy.orm import Session


class SearchService:
    async def search_products(
        self,
        db: Session,
        query: str | None = None,
        category_id: int | None = None,
        brand: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_rating: float | None = None,
        sort_by: str = "relevance",
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        cache_key = f"search:q={query}:cat={category_id}:brand={brand}:min_p={min_price}:max_p={max_price}:sort={sort_by}:p={page}:s={size}"
        cached_result = await cache_service.get_json(cache_key)
        if cached_result:
            return cached_result

        # Primary: OpenSearch query
        search_res = opensearch_manager.search_products(
            query_text=query,
            category_id=category_id,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            sort_by=sort_by,
            page=page,
            size=size,
        )

        # Fallback to PostgreSQL if OpenSearch returns no hits or is unavailable
        if search_res["total"] == 0 and not opensearch_manager.client:
            db_query = db.query(Product).filter(Product.status == ProductStatus.ACTIVE)
            if category_id:
                db_query = db_query.filter(Product.category_id == category_id)
            if brand:
                db_query = db_query.filter(Product.brand.ilike(f"%{brand}%"))
            if min_price:
                db_query = db_query.filter(Product.price >= min_price)
            if max_price:
                db_query = db_query.filter(Product.price <= max_price)
            if min_rating:
                db_query = db_query.filter(Product.rating >= min_rating)
            if query:
                db_query = db_query.filter(Product.name.ilike(f"%{query}%"))

            total = db_query.count()
            offset = (page - 1) * size
            products = db_query.offset(offset).limit(size).all()

            hits = [
                {
                    "id": p.id,
                    "sku": p.sku,
                    "name": p.name,
                    "description": p.description,
                    "category_id": p.category_id,
                    "brand": p.brand,
                    "price": float(p.price),
                    "currency": p.currency,
                    "rating": float(p.rating),
                    "status": p.status.value,
                }
                for p in products
            ]
            search_res = {"total": total, "hits": hits}

        await cache_service.set_json(cache_key, search_res, ttl_seconds=60)
        return search_res

search_service = SearchService()
