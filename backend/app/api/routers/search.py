from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.search_service import search_service

router = APIRouter(prefix="/products", tags=["Search"])

@router.get("/search")
async def search_products(
    q: Optional[str] = Query(None, description="Keyword text search query"),
    category_id: Optional[int] = Query(None, description="Category filter ID"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating filter"),
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
