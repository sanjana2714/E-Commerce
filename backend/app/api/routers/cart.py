from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.cart import CartResponse, CartItemAdd, CartItemUpdate, CartItemResponse
from app.services.cart_service import cart_service
from app.api.dependencies import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("", response_model=CartResponse)
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cart_service.get_cart_details(db, current_user.id)

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    item_in: CartItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_item = cart_service.add_item_to_cart(db, current_user.id, item_in)
    return {
        "id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
        "unit_price": float(cart_item.unit_price)
    }

@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    update_in: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_item = cart_service.update_cart_item(db, current_user.id, item_id, update_in)
    return {
        "id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
        "unit_price": float(cart_item.unit_price)
    }

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cart_service.remove_cart_item(db, current_user.id, item_id)
    return None

@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_service.clear_cart(db, current_user.id)
    return None
