from datetime import datetime

from app.db.models.product import ProductStatus
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str | None = None
    category_id: int
    brand: str
    price: float = Field(gt=0)
    currency: str = "USD"
    initial_stock: int = Field(default=0, ge=0)

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    brand: str | None = None
    price: float | None = Field(default=None, gt=0)
    status: ProductStatus | None = None
    stock_delta: int | None = None

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: str | None = None
    category_id: int
    brand: str
    price: float
    currency: str
    rating: float
    status: ProductStatus
    version: int
    stock_quantity: int | None = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedProductsResponse(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: list[ProductResponse]
