from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.product import ProductResponse

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)

class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product: Optional[ProductResponse] = None

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    items: List[CartItemResponse]

    model_config = ConfigDict(from_attributes=True)
