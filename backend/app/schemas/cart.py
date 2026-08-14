
from app.schemas.product import ProductResponse
from pydantic import BaseModel, ConfigDict, Field


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
    product: ProductResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    items: list[CartItemResponse]

    model_config = ConfigDict(from_attributes=True)
