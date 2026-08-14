from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.db.models.payment import PaymentStatus

class PaymentResponse(BaseModel):
    id: int
    payment_id: str
    order_id: int
    amount: float
    status: PaymentStatus
    transaction_reference: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaymentRetryRequest(BaseModel):
    simulate_failure: bool = False
