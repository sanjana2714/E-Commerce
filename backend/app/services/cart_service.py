from typing import Any

from app.core.exceptions import ResourceNotFoundError
from app.db.models.cart import Cart, CartItem
from app.db.models.product import Product
from app.schemas.cart import CartItemAdd, CartItemUpdate
from sqlalchemy.orm import Session


class CartService:
    def get_or_create_cart(self, db: Session, user_id: int) -> Cart:
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart

    def get_cart_details(self, db: Session, user_id: int) -> dict[str, Any]:
        cart = self.get_or_create_cart(db, user_id)
        total_amount = 0.0
        items_data = []

        for item in cart.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                item_total = float(product.price) * item.quantity
                total_amount += item_total
                items_data.append({
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(product.price),
                    "product": {
                        "id": product.id,
                        "sku": product.sku,
                        "name": product.name,
                        "brand": product.brand,
                        "price": float(product.price),
                        "currency": product.currency,
                        "rating": float(product.rating),
                        "status": product.status.value,
                    }
                })

        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "total_amount": round(total_amount, 2),
            "items": items_data
        }

    def add_item_to_cart(self, db: Session, user_id: int, item_in: CartItemAdd) -> CartItem:
        cart = self.get_or_create_cart(db, user_id)
        product = db.query(Product).filter(Product.id == item_in.product_id).first()
        if not product:
            raise ResourceNotFoundError(f"Product ID {item_in.product_id} not found.")

        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item_in.product_id
        ).first()

        if existing_item:
            existing_item.quantity += item_in.quantity
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=item_in.product_id,
                quantity=item_in.quantity,
                unit_price=product.price
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            return cart_item

    def update_cart_item(self, db: Session, user_id: int, item_id: int, update_in: CartItemUpdate) -> CartItem:
        cart = self.get_or_create_cart(db, user_id)
        item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if not item:
            raise ResourceNotFoundError(f"Cart item ID {item_id} not found.")

        item.quantity = update_in.quantity
        db.commit()
        db.refresh(item)
        return item

    def remove_cart_item(self, db: Session, user_id: int, item_id: int) -> bool:
        cart = self.get_or_create_cart(db, user_id)
        item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if not item:
            raise ResourceNotFoundError(f"Cart item ID {item_id} not found.")
        
        db.delete(item)
        db.commit()
        return True

    def clear_cart(self, db: Session, user_id: int):
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if cart:
            db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            db.commit()

cart_service = CartService()
