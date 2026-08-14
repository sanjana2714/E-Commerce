
from app.db.session import get_db
from app.services.search_service import search_service
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/products", tags=["Search"])

@router.get("/search")
async def search_products(
    q: str | None = Query(None, description="Keyword text search query"),
    category_id: int | None = Query(None, description="Category filter ID"),
    brand: str | None = Query(None, description="Brand filter"),
    min_price: float | None = Query(None, ge=0, description="Minimum price filter"),
    max_price: float | None = Query(None, ge=0, description="Maximum price filter"),
    min_rating: float | None = Query(None, ge=0, le=5, description="Minimum rating filter"),
    sort_by: str = Query("relevance", description="Sorting: relevance, price_asc, price_desc, rating_desc, newest"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    results = await search_service.search_products(
        db=db,
        query=q,
        category_id=category_id,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        size=size,
    )
    pages = (results["total"] + size - 1) // size if results["total"] > 0 else 0
    return {
        "total": results["total"],
        "page": page,
        "size": size,
        "pages": pages,
        "items": results["hits"]
    }
