from datetime import datetime

from app.db.models.order import OrderStatus
from app.schemas.product import ProductResponse
from pydantic import BaseModel, ConfigDict, Field


class OrderCreateItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    items: list[OrderCreateItem]

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float
    product: ProductResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    user_id: int
    idempotency_key: str
    status: OrderStatus
    total_amount: float
    currency: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
