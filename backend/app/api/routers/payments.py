from app.api.dependencies import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.payment import PaymentResponse, PaymentRetryRequest
from app.services.payment_service import payment_service
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/{order_id}/process", response_model=PaymentResponse)
def process_payment(
    order_id: int,
    req: PaymentRetryRequest = PaymentRetryRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return payment_service.process_simulated_payment(db, order_id, req.simulate_failure)

@router.post("/{order_id}/retry", response_model=PaymentResponse)
def retry_payment(
    order_id: int,
    req: PaymentRetryRequest = PaymentRetryRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return payment_service.process_simulated_payment(db, order_id, req.simulate_failure)

@router.get("/{order_id}", response_model=PaymentResponse)
def get_payment_details(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return payment_service.get_payment(db, order_id)
