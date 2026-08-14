from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    CategoryCreate,
    CategoryResponse,
    PaginatedProductsResponse,
)
from app.services.product_service import product_service
from app.api.dependencies import require_role
from app.db.models.user import UserRole, User

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    cat_in: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return product_service.create_category(db, cat_in)

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return product_service.list_categories(db)

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    prod_in: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return product_service.create_product(db, prod_in)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)
    stock_qty = product.inventory.stock_quantity if product.inventory else 0
    res = ProductResponse.model_validate(product)
    res.stock_quantity = stock_qty
    return res

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    prod_in: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    product = product_service.update_product(db, product_id, prod_in)
    stock_qty = product.inventory.stock_quantity if product.inventory else 0
    res = ProductResponse.model_validate(product)
    res.stock_quantity = stock_qty
    return res

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN]))
):
    product_service.delete_product(db, product_id)
    return None
