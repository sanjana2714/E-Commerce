from datetime import datetime

from app.db.models.payment import PaymentStatus
from pydantic import BaseModel, ConfigDict


class PaymentResponse(BaseModel):
    id: int
    payment_id: str
    order_id: int
    amount: float
    status: PaymentStatus
    transaction_reference: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaymentRetryRequest(BaseModel):
    simulate_failure: bool = False
