from app.core.exceptions import DuplicateRequestError, ResourceNotFoundError
from app.db.models.inventory import Inventory
from app.db.models.product import Category, Product, ProductStatus
from app.events.types import EventType
from app.schemas.product import CategoryCreate, ProductCreate, ProductUpdate
from app.services.outbox_service import outbox_service
from sqlalchemy.orm import Session


class ProductService:
    def create_category(self, db: Session, cat_in: CategoryCreate) -> Category:
        existing = db.query(Category).filter(Category.name == cat_in.name).first()
        if existing:
            raise DuplicateRequestError(f"Category '{cat_in.name}' already exists.")
        slug = cat_in.name.lower().replace(" ", "-")
        category = Category(name=cat_in.name, slug=slug, description=cat_in.description)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def list_categories(self, db: Session) -> list[Category]:
        return db.query(Category).all()

    def create_product(self, db: Session, prod_in: ProductCreate) -> Product:
        existing = db.query(Product).filter(Product.sku == prod_in.sku).first()
        if existing:
            raise DuplicateRequestError(f"Product with SKU '{prod_in.sku}' already exists.")
        
        category = db.query(Category).filter(Category.id == prod_in.category_id).first()
        if not category:
            raise ResourceNotFoundError(f"Category ID {prod_in.category_id} not found.")

        product = Product(
            sku=prod_in.sku,
            name=prod_in.name,
            description=prod_in.description,
            category_id=prod_in.category_id,
            brand=prod_in.brand,
            price=prod_in.price,
            currency=prod_in.currency,
            status=ProductStatus.ACTIVE,
            version=1
        )
        db.add(product)
        db.flush()

        # Initialize Inventory record
        inventory = Inventory(
            product_id=product.id,
            stock_quantity=prod_in.initial_stock,
            reserved_quantity=0,
            version=1
        )
        db.add(inventory)

        # Generate Outbox Event
        prod_payload = {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "category_id": product.category_id,
            "brand": product.brand,
            "price": float(product.price),
            "currency": product.currency,
            "rating": float(product.rating),
            "status": product.status.value,
            "initial_stock": prod_in.initial_stock,
        }
        outbox_service.create_outbox_event(
            db=db,
            aggregate_type="Product",
            aggregate_id=str(product.id),
            event_type=EventType.PRODUCT_CREATED.value,
            payload=prod_payload
        )

        db.commit()
        db.refresh(product)
        return product

    def get_product(self, db: Session, product_id: int) -> Product:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ResourceNotFoundError(f"Product ID {product_id} not found.")
        return product

    def update_product(self, db: Session, product_id: int, prod_in: ProductUpdate) -> Product:
        product = self.get_product(db, product_id)
        
        if prod_in.name is not None:
            product.name = prod_in.name
        if prod_in.description is not None:
            product.description = prod_in.description
        if prod_in.category_id is not None:
            product.category_id = prod_in.category_id
        if prod_in.brand is not None:
            product.brand = prod_in.brand
        if prod_in.price is not None:
            product.price = prod_in.price
        if prod_in.status is not None:
            product.status = prod_in.status
        
        product.version += 1

        if prod_in.stock_delta is not None and product.inventory:
            product.inventory.stock_quantity = max(0, product.inventory.stock_quantity + prod_in.stock_delta)

        # Outbox event
        prod_payload = {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "category_id": product.category_id,
            "brand": product.brand,
            "price": float(product.price),
            "currency": product.currency,
            "rating": float(product.rating),
            "status": product.status.value,
            "version": product.version,
        }
        outbox_service.create_outbox_event(
            db=db,
            aggregate_type="Product",
            aggregate_id=str(product.id),
            event_type=EventType.PRODUCT_UPDATED.value,
            payload=prod_payload
        )

        db.commit()
        db.refresh(product)
        return product

    def delete_product(self, db: Session, product_id: int) -> bool:
        product = self.get_product(db, product_id)
        product.status = ProductStatus.DISCONTINUED
        
        outbox_service.create_outbox_event(
            db=db,
            aggregate_type="Product",
            aggregate_id=str(product.id),
            event_type=EventType.PRODUCT_DELETED.value,
            payload={"id": product.id, "status": product.status.value}
        )

        db.commit()
        return True

product_service = ProductService()
