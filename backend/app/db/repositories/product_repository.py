
from app.db.models.product import Category, Product, ProductStatus
from sqlalchemy.orm import Session


class ProductRepository:
    def get_by_id(self, db: Session, product_id: int) -> Product | None:
        return db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, db: Session, sku: str) -> Product | None:
        return db.query(Product).filter(Product.sku == sku).first()

    def list_products(
        self,
        db: Session,
        category_id: int | None = None,
        brand: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        skip: int = 0,
        limit: int = 50
    ) -> list[Product]:
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

    def get_category_by_id(self, db: Session, category_id: int) -> Category | None:
        return db.query(Category).filter(Category.id == category_id).first()

    def list_categories(self, db: Session) -> list[Category]:
        return db.query(Category).all()

product_repository = ProductRepository()
