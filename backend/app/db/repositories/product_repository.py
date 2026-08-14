from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.product import Product, Category, ProductStatus

class ProductRepository:
    def get_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, db: Session, sku: str) -> Optional[Product]:
        return db.query(Product).filter(Product.sku == sku).first()

    def list_products(
        self,
        db: Session,
        category_id: Optional[int] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Product]:
        query = db.query(Product).filter(Product.status == ProductStatus.ACTIVE)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, product: Product) -> Product:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def get_category_by_id(self, db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    def list_categories(self, db: Session) -> List[Category]:
        return db.query(Category).all()

product_repository = ProductRepository()
