from typing import Any

from app.db.session import get_db
from app.services.analytics_service import analytics_service
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/analytics", tags=["Analytics & DSA"])

@router.get("/top-products", response_model=list[dict[str, Any]])
def get_top_k_products(
    k: int = Query(10, ge=1, le=100, description="Top K elements count"),
    db: Session = Depends(get_db)
):
    """
    Returns Top-K products sorted by total sales quantity using an efficient O(N log K) Min-Heap algorithm.
    """
    return analytics_service.get_top_k_products(db, k=k)
