from typing import List, Optional
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order_service import order_service
from app.api.dependencies import get_current_user, require_role
from app.db.models.user import User, UserRole
from app.core.exceptions import ValidationError

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not idempotency_key or not idempotency_key.strip():
        raise ValidationError("Header 'Idempotency-Key' is required for idempotent order placement.")
    
    return order_service.create_order_idempotent(
        db=db,
        user_id=current_user.id,
        idempotency_key=idempotency_key.strip(),
        order_in=order_in
    )

@router.get("", response_model=List[OrderResponse])
def list_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.list_orders_for_user(db, current_user.id)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Admins can view any order, users can view their own
    user_filter = None if current_user.role == UserRole.ADMIN else current_user.id
    return order_service.get_order(db, order_id, user_id=user_filter)

@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return order_service.transition_order_status(db, order_id, status_update.status)
