from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.product import ProductStatus

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category_id: int
    brand: str
    price: float = Field(gt=0)
    currency: str = "USD"
    initial_stock: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    status: Optional[ProductStatus] = None
    stock_delta: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    category_id: int
    brand: str
    price: float
    currency: str
    rating: float
    status: ProductStatus
    version: int
    stock_quantity: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedProductsResponse(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: List[ProductResponse]
